import pandas as pd
import os
import re

# 1. Header Mapping (Every possible Japanese header we've seen)
HEADER_MAP = {
    "title": "Project Title",
    "date": "Report Date",
    "link": "URL",
    "thumbnail": "Thumbnail URL",
    "main_image": "Main Image URL",
    "description": "Description",
    "gallery": "Gallery URLs",
    "完工年月": "Completion Month/Year",
    "場所": "Location",
    "建物種別": "Building Type",
    "受注形態": "Contract Type",
    "完工年月日": "Completion Date",
    "工事内容": "Work Details",
    "完成年月日": "Completion Date",
    "建物": "Building Info",
    "備考": "Remarks"
}

# 2. Comprehensive Value Mapping
VALUE_MAP = {
    # Prefectures & Major Regions
    "東京都": "Tokyo", "神奈川県": "Kanagawa", "千葉県": "Chiba", "埼玉県": "Saitama",
    "茨城県": "Ibaraki", "栃木県": "Tochigi", "群馬県": "Gunma", "静岡県": "Shizuoka",
    "大阪府": "Osaka", "兵庫県": "Hyogo", "愛知県": "Aichi", "宮城県": "Miyagi",
    "石川県": "Ishikawa", "岡山県": "Okayama", "広島県": "Hiroshima", "北海道": "Hokkaido",
    "東北地方": "Tohoku Region",
    
    # Specific Cities/Wards/Areas (Extended)
    "荒川": "Arakawa", "中野": "Nakano", "中央": "Chuo", "江戸川": "Edogawa",
    "新宿": "Shinjuku", "渋谷": "Shibuya", "港": "Minato", "台東": "Taito",
    "江東": "Koto", "墨田": "Sumida", "品川": "Shinagawa", "目黒": "Meguro",
    "大田": "Ota", "世田谷": "Setagaya", "杉並": "Suginami", "豊島": "Toshima",
    "北": "Kita", "板橋": "Itabashi", "練馬": "Nerima", "足立": "Adachi",
    "葛飾": "Katsushika", "西葛西": "Nishi-Kasai", "西早稲田": "Nishi-Waseda",
    "西麻布": "Nishi-Azabu", "六本木通り": "Roppongi-dori", "銀座": "Ginza",
    "新橋": "Shinbashi", "八重洲": "Yaesu", "日本橋": "Nihonbashi", "赤羽": "Akabane",
    "芝大門": "Shiba-daimon", "月島": "Tsukishima", "深川": "Fukagawa",
    "金沢": "Kanazawa", "横浜": "Yokohama", "川崎": "Kawasaki", "相模原": "Sagamihara",
    "さいたま": "Saitama", "越谷": "Koshigaya", "八潮": "Yashio", "つくば": "Tsukuba",
    "府中": "Fuchu", "武蔵村山": "Musashimurayama", "東習志野": "Higashi-Narashino",
    "東恋ヶ窪": "Higashi-Koigakubo", "保谷町": "Hoya-cho", "上福岡": "Kamifukuoka",
    "三崎町": "Misaki-cho", "錦町": "Nishiki-cho", "湘南": "Shonan", "大森": "Omori",
    "弘明寺": "Gumyoji", "後楽園": "Korakuen", "新砂": "Shinsuna", "東新井": "Higashi-Arai",
    "東池袋": "Higashi-Ikebukuro", "西日暮里": "Nishi-Nippori", "東陽": "Toyo",
    "下目黒": "Shimomeguro", "中央林間": "Chuo-Rinkan", "五反田": "Gotanda",
    "京橋": "Kyobashi", "外神田": "Soto-Kanda", "多摩川": "Tamagawa", "下目黒": "Shimomeguro",
    "弦巻": "Tsurumaki", "深川": "Fukagawa", "岩槻": "Iwatsuki", "越谷": "Koshigaya",
    "朝霞": "Asaka", "春": "Kasuga", "佐賀": "Saga", "新川崎": "Shin-Kawasaki",
    "池袋": "Ikebukuro", "東武": "Tobu", "西": "Nishi", "東": "Higashi", "南": "Minami",
    "高洲": "Takasu", "舞岡": "Maioka", "王子": "Oji", "勝島": "Katsushima",
    "東雲": "Shinonome", "囲町": "Kakoi-cho", "東習志野": "Higashi-Narashino",
    "飯能": "Hanno", "習志野": "Narashino", "西暮里": "Nishi-Nippori", "仙台": "Sendai",
    "町": "Town", "地": "Area", "駅前": "Station-front", "周辺": "Surrounding",
    "江ノ島": "Enoshima", "深川": "Fukagawa",
    
    # Project & Technical Terms (Extended)
    "（仮称）": "(Tentative name) ", "(仮称)": "(Tentative name) ", "（仮称)": "(Tentative name) ", "仮称": "Tentative Name",
    "新築": "New Construction", "新": "New ", "既存建物": "Existing Building", "既存": "Existing",
    "現存建物": "Existing Building", "現存": "Existing",
    "に伴う": " accompanying ", "に伴う": " accompanying ",
    "とりこわし": " Demolition", "とりこわし工事": " Demolition Work",
    "撤去": " Removal", "アスベスト": "Asbestos", "アスベスト撤去": "Asbestos Removal",
    "アスベスト除去": "Asbestos Removal", "現状回復": "Site Restoration",
    "建替え": "Rebuilding", "建替": "Rebuilding",
    "整備": "Development/Maintenance", "区画整理": "Land Readjustment",
    "土": "Land ", "跡": " site", "跡地": " Site", "のみ": " only", "の為の": " for ",
    "その他": " and other ", "他": " & others", "旧": "Former ",
    "本館": " Main Building", "別館": " Annex", "支店": " Branch", "支社": " Branch Office", "支所": " Branch Office",
    "店": " Store", "店舗": " Store/Retail", "舗": "",
    "プロジェクト": " Project", "PJ": " Project", "Plan/Project": "Project/Plan", "プロジェクト": "Project",
    "基礎": " Foundation", "土間": " Earth Floor/Concrete Floor",
    "地上": "Above-ground", "地下": "Below-ground", "部": " part", "地上部": "Above-ground part", "地下部": "Below-ground part",
    "株式会社": "Co., Ltd.", "株式Company": "Co., Ltd.", "株式": "Co., Ltd.", "㈱": " Co., Ltd.",
    "有限会社": "Ltd.", "（有）": "Ltd.",
    "学校": "School", "中": "Junior High", "高": "High", "大学": "University", "高等School": "High School",
    "校舎": "School Building", "学生": "Student", "法学部": "Faculty of Law", "３号館": "Building No. 3",
    "病院": "Hospital", "クリニック": "Clinic", "総合Hospital": "General Hospital", "聖": "St. ",
    "総合": "General", "聖ヨゼフ": "St. Joseph", "聖テレジア会": "St. Theresa Society",
    "百貨店": "Department Store",
    "ホテル": "Hotel", "Hotel": "Hotel", "旅館": "Inn/Japanese Hotel", "宿泊": "Accommodation",
    "ビジネスホテル": "Business Hotel",
    "社員寮": "Employee Dormitory", "寮": "Dormitory", "学生寮": "Student Dormitory", "社宅": "Company Housing",
    "住宅": "Housing", "団地": "Housing Complex", "マンション": "Apartment/Condo", "アパート": "Apartment", "戸建て": "Detached House",
    "集合住宅": "Housing Complex", "共同住宅": "Shared Housing", "集合Housing": "Housing Complex", "共同Housing": "Shared Housing",
    "スーパー": "Supermarket", "マーケット": "Market", "百貨店": "Department Store",
    "ゴルフ練習場": "Golf Driving Range", "ボウリング場": "Bowling Alley",
    "ビデオスタジオ": "Video Studio", "スタジオ": "Studio", "Studio": "Studio",
    "ブックセンター": "Book Center", "家電量販店": "Electronics Store", "精肉センター": "Meat Processing Center",
    "物流": "Logistics", "運輸": "Transport", "運送会社": "Transport Company", "運送": "Transport",
    "製作所": "Manufacturing Plant", "製作 Office/Plant": "Manufacturing Plant", "製作": "Manufacturing",
    "製鋼": "Steelmaking", "製紙": "Papermaking", "鍛造": "Forging",
    "薬品": "Pharmaceuticals", "薬": "Pharmaceutical", "クリーン": "Clean",
    "銀行": "Bank", "支店": "Branch",
    "官公庁": "Government Office", "官庁": "Government Office",
    "社会福祉法人": "Social Welfare Corporation",
    "一丁目": " 1-chome", "二丁目": " 2-chome", "三丁目": " 3-chome", "四丁目": " 4-chome", "五丁目": " 5-chome",
    "六丁目": " 6-chome", "七丁目": " 7-chome", "八丁目": " 8-chome",
    "1丁目": " 1-chome", "2丁目": " 2-chome", "3丁目": " 3-chome", "4丁目": " 4-chome", "5丁目": " 5-chome",
    "１丁目": " 1-chome", "２丁目": " 2-chome", "３丁目": " 3-chome", "４丁目": " 4-chome", "５丁目": " 5-chome",
    "6丁目": " 6-chome", "7丁目": " 7-chome", "8丁目": " 8-chome",
    "支店": "Branch", "号館": "Building No. ", "号棟": "Building No. ",
    
    # Specific Company/Building Names
    "名鉄運輸": "Meitetsu Transport", "名鉄": "Meitetsu", "いなげや": "Inageya", "ピアゴ": "Piago",
    "ホテルオークラ東京": "Hotel Okura Tokyo", "オークラ": "Okura",
    "丸広百貨店": "Maruhiro Department Store", "丸広": "Maruhiro", "飯能": "Hanno",
    "ジューテック": "Jutec", "シノテスト": "Sinotest", "ランドポート": "Landport", "Landport": "Landport",
    "サニーサイドヒル": "Sunnyside Hill", "サンイースト": "Suneast", "イメージスタジオ": "Image Studio",
    "東テク": "Totech", "新立川航空機": "Shin Tachikawa Aircraft", "国永紙業": "Kuninaga Paper",
    "昭和女子大": "Showa Women's University", "本大学": "Nihon University", "日本大学": "Nihon University",
    "埼玉栄": "Saitama Sakae", "プリンスホテル": "Prince Hotel", "浅羽": "Asaba", "興和": "Kowa",
    
    # Structural & Action Terms
    "解体工事": " Demolition Work", "解体": " Demolition",
    "工事": " Work/Construction", "内容": " Details",
    "駐車場": " Parking Lot", "整地": " Land Leveling",
    "事業": " Project", "計画": " Project/Plan",
    "第一種": " Type 1", "市街地": " Urban Area", "再開発": " Redevelopment",
    "土木": " Civil Engineering",
    "オフィス": " Office", "ビル": " Building", "事務所": " Office",
    "センター": " Center", "倉庫": " Warehouse",
    "工場": " Factory", "所": " Plant/Office", "営業所": " Business Office", "営業 Plant/Office": " Business Office",
    "本社": " Headquarters", "本部": " Headquarters", "建屋": " Building", "施設": " Facility",
    "区": " Ward", "市": " City", "村": " Village", "地 Ward": "District/Area",
    "某": "Certain/Unnamed ",
    "及び": " and ", "および": " and ", "等": " etc.",
    "他": " & others", "兼": " and ", "体": "",
    "工事中": "Under Construction", "備考": "Remarks", "移転": "Relocation",
    "本青-館": "Main Building etc.", "商業": "Commercial",
    
    # General Suffixes & Artifacts
    "年": "-", "月": "-", "日": "",
    "　": " ", "・": " & ", "、": ", ", "。": ". ", "㈱": " Co., Ltd.", "（": "(", "）": ")", "(": "(", ")": ")"
}

JP_REGEX = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]')

def translate_any_cell(text, mapping):
    if not isinstance(text, str) or pd.isna(text):
        return text
    
    # 1. Direct Match
    if text in mapping:
        return mapping[text]
    
    # 2. Sequential Replacement (Handle phrases like "荒川区解体工事")
    # We sort keys by length (longest first) to avoid partial replacement bugs
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    
    result = text
    for jp in sorted_keys:
        if jp in result:
            result = result.replace(jp, mapping[jp])
    
    return result

def main():
    input_file = "tanaken_projects.csv"
    output_file = "tanaken_projects_english.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file, encoding="utf-8-sig")

    # A. Translate Headers
    df.rename(columns=HEADER_MAP, inplace=True)
    
    # B. Translate EVERY cell in the dataframe
    print("Translating all cells (this might take a moment)...")
    for col in df.columns:
        # We skip URL columns to avoid breaking links
        if "URL" in col or "link" in col or "thumbnail" in col or "image" in col or "gallery" in col:
            continue
        
        df[col] = df[col].apply(lambda x: translate_any_cell(x, VALUE_MAP))

    # C. Save
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"\nSuccess! Fully translated data saved to '{output_file}'.")

    # D. Validation Check
    remaining_jp = []
    for col in df.columns:
        if "URL" in col or "link" in col: continue
        for val in df[col].dropna():
            if isinstance(val, str) and JP_REGEX.search(val):
                remaining_jp.append(val)
    
    if remaining_jp:
        print(f"\nFound {len(set(remaining_jp))} unique strings that still contain Japanese characters.")
        print("Example untranslated fragments:")
        for item in sorted(list(set(remaining_jp)))[:10]:
            print(f"  - {item}")
    else:
        print("\nVerification Complete: No Japanese characters found in non-URL columns!")

if __name__ == "__main__":
    main()
