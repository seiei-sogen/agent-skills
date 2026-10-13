# ローカル専用。5100 番の admin（auto_reserve_development）で「Google Map 閉業の紐付け確認」を手で試すためのダミーデータを作る。
# 何度流しても同じ状態に戻る（前回作った分と 10-07 の local-check-* を消してから作る）。CLEANUP=1 を付けると消すだけ。
# place_id は架空なので、Google マップへのリンクを開いても店は出ない。バッチを本実行すると閉業 place の取得に失敗する。
#
# 実行（worktree のルートで）:
#   DISABLE_SPRING=1 bin/rails runner docs/req/issue45412-backend-relink-closed-google-maps/check/seed-check-data.rb

abort "development でだけ動かす（今は #{Rails.env}）" unless Rails.env.development?

# ダミーデータを作るときのコールバックが積むジョブ（翻訳など）を、Redis にも外部にも出さない
require "sidekiq/testing"
Sidekiq::Testing.fake!
ActiveJob::Base.queue_adapter = :test

require "factory_bot"
FactoryBot.definition_file_paths = [Rails.root.join("spec/factories").to_s]
FactoryBot.find_definitions
include FactoryBot::Syntax::Methods

PREFIX = "kakunin45412-".freeze
NAME_PREFIX = "【閉業確認用】".freeze
PLACE_ID_PATTERNS = ["#{PREFIX}%", "local-check-%"].freeze
ADMIN = "http://admin.lvh.me:5100".freeze
NOW = Time.current

# ---- 前回の分を消す（店舗は残して使い回す） ----------------------------------------
# 画面で実在の place へ付け替えた後も作り直せるよう、確認用の店舗の Google Map 紐付けは全部消す
RestaurantWebSystem.google_map.where(restaurant: Restaurant.where("name LIKE ?", "#{NAME_PREFIX}%")).delete_all
PLACE_ID_PATTERNS.each do |pattern|
  GoogleMap::ClosedPlaceCheck.where("closed_google_place_id LIKE ?", pattern).delete_all
  RestaurantWebSystem.where("url LIKE ?", "%place_id:#{pattern}").delete_all
  GoogleMap::Restaurant.where("google_place_id LIKE ?", pattern).delete_all
end

# CLEANUP=1 なら消すだけで終える。店舗の行は残し、未解決の一覧やバッチの対象に出ないよう非公開にする
if ENV["CLEANUP"]
  n = Restaurant.where("name LIKE ?", "#{NAME_PREFIX}%").update_all(status: Restaurant.statuses[:unpublished])
  puts "ダミーの紐付け・place・再チェック記録を消し、店舗 #{n} 件を非公開にした"
  exit
end

# ---- 道具 ------------------------------------------------------------------------
# factory の owner と city は共有 dev DB の既存データと一意制約で衝突するので、既存の行を渡す
TEMPLATE = Restaurant.where("name LIKE ?", "#{NAME_PREFIX}%").first
OWNER = TEMPLATE&.owner || Owner.order(:id).first
CITY = TEMPLATE&.city || City.order(:id).first

def restaurant_named(name, index)
  Restaurant.find_by(name:) || begin
    r = create(:restaurant, owner: OWNER, city: CITY, skip_phone_system: true, status: :published, name_i18n_ja: name,
      phone_number: format("+813123450%02d", index), latitude: 35.6 + (index * 0.05), longitude: 139.7)
    # factory の既定の status は unpublished なので公開に直す
    r.update!(status: :published, for_test: false, open_status: :open)
    r
  end
end

# 本物の RestaurantSaver と同じ形で google_map_restaurants に保存する
def save_place(place_id, name:, phone_number:, open_status:, address: "東京都中央区築地4-1")
  place = GoogleMap::Restaurant.find_or_initialize_by(google_place_id: place_id)
  GoogleMap::RestaurantMultiLocaleInfoFetcher::TARGET_LOCALES.each do |locale|
    I18n.with_locale(locale) do
      place.name = name
      place.address = address
    end
  end
  place.assign_attributes(country_code: "jp", phone_number:, crawled_at: NOW,
    data: { "open_status" => open_status, "coordinates" => { "latitude" => 35.66, "longitude" => 139.77 } })
  place.save!
  place
end

def check_id(n) = format("45412000-0000-4000-8000-%012d", n)

Scenario = Struct.new(:n, :key, :name, :result, :count, :checked_days_ago, :failure_reason, :candidates, :note, keyword_init: true)
# candidates: [place_id の末尾, 保存するか, 店名]。保存しない候補は画面で「未取得」になる
SCENARIOS = [
  Scenario.new(n: 1, key: "K1", name: "海鮮居酒屋 湊", result: :multiple_matches, count: 1, checked_days_ago: 1,
    candidates: [["a", true, "海鮮居酒屋 湊"], ["b", true, "海鮮居酒屋 湊 築地店"], ["c", false, nil]],
    note: "候補から付け替える。c は未取得なので入力欄へ案内される"),
  Scenario.new(n: 2, key: "K2", name: "喫茶 やまびこ", result: :no_search_results, count: 1, checked_days_ago: 2, candidates: [],
    note: "検索結果なし。入力欄で付け替える"),
  Scenario.new(n: 3, key: "K3", name: "蕎麦処 ふじ", result: :no_match, count: 2, checked_days_ago: 3,
    candidates: [["other", true, "ラーメン 藤"]], note: "2回目の付け替えなし。次は14日後"),
  Scenario.new(n: 4, key: "K4", name: "焼肉 ほし", result: :too_many_candidates, count: 3, checked_days_ago: 4, candidates: [],
    note: "3回目。次は28日後。対応不要にする"),
  Scenario.new(n: 5, key: "K5", name: "洋食 さくら", result: :already_referenced, count: 4, checked_days_ago: 5,
    candidates: [["ref", true, "洋食 さくら"]], note: "4回目。次は56日後。候補はほかの紐付けが参照している"),
  Scenario.new(n: 6, key: "K6", name: "中華 りゅう", result: :no_match, count: 5, checked_days_ago: 6, candidates: [],
    note: "5回目。次は90日後"),
  Scenario.new(n: 7, key: "K7", name: "パン工房 こむぎ", result: :failed, count: 1, checked_days_ago: 8, failure_reason: :closed_place_fetch_failed,
    candidates: [], note: "失敗。予定（7日後）を過ぎているので、バッチの対象になる"),
].freeze

rows = SCENARIOS.map do |s|
  restaurant = restaurant_named("#{NAME_PREFIX}#{s.name}", s.n)
  closed_id = "#{PREFIX}#{s.key}-closed"
  save_place(closed_id, name: restaurant.name, phone_number: restaurant.phone_number, open_status: "permanently_closed")
  restaurant.restaurant_web_systems.create!(url: GoogleMap::Restaurant.canonical_url(closed_id))
  candidate_ids = s.candidates.map do |suffix, saved, name|
    "#{PREFIX}#{s.key}-#{suffix}".tap do |id|
      save_place(id, name:, phone_number: restaurant.phone_number, open_status: "open") if saved
    end
  end
  checked_at = NOW - s.checked_days_ago.days
  check = GoogleMap::ClosedPlaceCheck.create!(
    id: check_id(s.n), restaurant:, closed_google_place_id: closed_id, result: s.result, failure_reason: s.failure_reason,
    consecutive_unrelinked_count: s.count, checked_at:, candidate_google_place_ids: candidate_ids,
    next_recheck_at: checked_at + GoogleMap::ClosedPlaceCheck.recheck_interval(s.count),
  )
  [s, restaurant, check]
end

# K5 の候補を、別の店の archived な紐付け行が指している状態にする
other = restaurant_named("#{NAME_PREFIX}洋食 さくら（移転前の登録）", 8)
other.restaurant_web_systems.create!(url: GoogleMap::Restaurant.canonical_url("#{PREFIX}K5-ref"), status: :archived)

# ---- 結果 ------------------------------------------------------------------------
puts "DB: #{ActiveRecord::Base.connection.current_database}  作成時刻: #{NOW.strftime('%Y-%m-%d %H:%M')}"
puts
rows.each do |s, restaurant, check|
  puts "#{s.key} #{restaurant.name}（restaurant_id=#{restaurant.id}）"
  puts "   #{ADMIN}/google_map_closed_place_checks/#{check.id}"
  puts "   最後の結果=#{check.result_i18n}#{check.failure_reason ? "（#{check.failure_reason_i18n}）" : ''}  回数=#{check.consecutive_unrelinked_count}  " \
       "最後の再チェック=#{I18n.l(check.checked_at, format: :long)}  次の予定=#{I18n.l(check.next_recheck_at, format: :long)}"
  puts "   #{s.note}"
end
unresolved = GoogleMap::ClosedPlaceCheck.unresolved
puts
puts "一覧（未解決）に出る組: #{unresolved.count} 件、そのうち予定を過ぎてバッチの対象になる組: #{unresolved.where(next_recheck_at: ..NOW).count} 件"
puts "一覧: #{ADMIN}/google_map_closed_place_checks"
