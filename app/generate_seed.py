#!/usr/bin/env python3
"""Generate seed_products.sql from scraped product data."""
import json, re

# ── Color mapping ──
def map_color(raw):
    raw = (raw or '').lower().strip()
    if not raw or raw in ('n/a', 'more colors', '00', '09'): return 'black'
    if raw in ('01',): return 'white'
    if raw in ('cream', 'vanilla', 'light beige', 'light beige/patterned'): return 'beige'
    for c in ['black', 'white', 'gray', 'blue', 'red', 'beige', 'green', 'navy', 'brown', 'pink', 'yellow', 'purple']:
        if c in raw: return c
    if 'burgundy' in raw: return 'red'
    if 'orange' in raw or 'rust' in raw: return 'brown'
    if 'charcoal' in raw: return 'gray'
    if 'mid-blue' in raw or 'pastel blue' in raw: return 'blue'
    if 'navy' in raw: return 'navy'
    if 'silver' in raw or 'gold' in raw or 'metallic' in raw: return 'beige'
    if '65' in raw or '67' in raw or '69' in raw: return 'blue'  # Uniqlo denim codes
    if '05' in raw or '08' in raw: return 'gray'
    if '30' in raw or '31' in raw or '32' in raw or '33' in raw: return 'beige'
    if '37' in raw or '39' in raw: return 'brown'
    if '35' in raw or '36' in raw: return 'brown'
    if '50' in raw: return 'green'
    if '58' in raw or '57' in raw: return 'green'
    if '61' in raw or '63' in raw: return 'blue'
    if '68' in raw or '72' in raw or '74' in raw: return 'brown'
    if '70' in raw: return 'brown'
    if '10' in raw or '12' in raw or '15' in raw or '17' in raw: return 'pink'
    return 'black'

def parse_price(raw):
    m = re.search(r'[\d.]+', (raw or '0').replace(',',''))
    return float(m.group()) if m else 0

def esc(s):
    return (s or '').replace("'", "''")

TRANSPARENT = 'transparent-background.png'

# ── All scraped products ──
products = []

# H&M
for p in [
    {"name":"Oversized Tunic Dress","price":"24.99","color":"beige","cat":"Dress","image_url":"https://image.hm.com/assets/hm/d9/7d/d97d438caf7f4e93a2c583f4e5d944d426bde168.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1333212001.html"},
    {"name":"Oversized Tunic Dress","price":"24.99","color":"brown","cat":"Dress","image_url":"https://image.hm.com/assets/hm/4b/66/4b667cc7caebc712638a1506096923515f386f14.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1335611002.html"},
    {"name":"Belted Linen-Blend Shorts","price":"39.99","color":"beige","cat":"Shorts","image_url":"https://image.hm.com/assets/hm/45/93/4593346b68074b34cb8ead9a349e127a07f553fb.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1317532001.html"},
    {"name":"Oversized Blouse","price":"39.99","color":"blue","cat":"Shirt","image_url":"https://image.hm.com/assets/hm/91/76/9176c55243ed97e52a22b1a326d488ba0de84624.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1334167002.html"},
    {"name":"Smocked Dress with Flared Skirt","price":"39.99","color":"beige","cat":"Dress","image_url":"https://image.hm.com/assets/hm/3b/50/3b50a516df8249a3f9c8426590be4ed901c6c77b.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1333122001.html"},
    {"name":"Lace-Trimmed Satin Slip Dress","price":"39.99","color":"white","cat":"Dress","image_url":"https://image.hm.com/assets/hm/b5/0b/b50bbeae0a8c615ebade938fe21d35ac797101d9.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1334652001.html"},
    {"name":"Coated Jacket","price":"39.99","color":"brown","cat":"Jacket","image_url":"https://image.hm.com/assets/hm/b9/8e/b98e95e52bb0f63d1423cb5cca75a7a7e4fa6eee.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1328847003.html"},
    {"name":"Open-Back Halterneck Dress","price":"39.99","color":"pink","cat":"Dress","image_url":"https://image.hm.com/assets/hm/af/a1/afa15d0a86003d9361ba36aa1cd2275fc2776a9a.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1321002002.html"},
    {"name":"Pointelle-Knit Cardigan","price":"39.99","color":"beige","cat":"Sweater","image_url":"https://image.hm.com/assets/hm/a8/0e/a80ea901044d2996c20b8d53edb9fd9d6eaf8d23.jpg?imwidth=1536","url":"https://www2.hm.com/en_ca/productpage.1332156003.html"},
]:
    products.append({**p, "brand":"H&M", "style":"casual"})

# Uniqlo Tops
for name, price, color, url, img in [
    ("Mini Short Sleeve T-Shirt",14.90,"black","https://www.uniqlo.com/ca/en/products/E465760-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/465760/item/cagoods_69_465760_3x4.jpg?width=300"),
    ("Ribbed Mini T-Shirt",14.90,"black","https://www.uniqlo.com/ca/en/products/E484457-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484457/item/cagoods_50_484457_3x4.jpg?width=300"),
    ("Striped Mini T-Shirt",14.90,"white","https://www.uniqlo.com/ca/en/products/E483535-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483535/item/cagoods_01_483535_3x4.jpg?width=300"),
    ("AIRism Cotton Oversized T-Shirt",19.90,"brown","https://www.uniqlo.com/ca/en/products/E465185-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/465185/item/cagoods_69_465185_3x4.jpg?width=300"),
]:
    products.append({"name":name,"brand":"UNIQLO","cat":"T-shirt","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Uniqlo Bottoms
for name, price, cat, color, url, img in [
    ("Baggy Jeans",49.90,"Jeans","blue","https://www.uniqlo.com/ca/en/products/E483999-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483999/item/cagoods_67_483999_3x4.jpg?width=300"),
    ("Straight Jeans Embroidered",59.90,"Jeans","blue","https://www.uniqlo.com/ca/en/products/E482279-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482279/item/cagoods_69_482279_3x4.jpg?width=300"),
    ("Straight Jeans Printed Logo",59.90,"Jeans","blue","https://www.uniqlo.com/ca/en/products/E476209-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/476209/item/cagoods_65_476209_3x4.jpg?width=300"),
    ("Straight Jeans Tall",59.90,"Jeans","blue","https://www.uniqlo.com/ca/en/products/E477334-001/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/477334001/item/cagoods_65_477334001_3x4.jpg?width=300"),
    ("Denim Shorts",49.90,"Shorts","blue","https://www.uniqlo.com/ca/en/products/E483512-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483512/item/cagoods_69_483512_3x4.jpg?width=300"),
    ("EZY Wide Straight Jeans",59.90,"Jeans","blue","https://www.uniqlo.com/ca/en/products/E482281-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482281/item/cagoods_69_482281_3x4.jpg?width=300"),
    ("Barrel Jeans Tall",59.90,"Jeans","black","https://www.uniqlo.com/ca/en/products/E484807-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484807/item/cagoods_00_484807_3x4.jpg?width=300"),
    ("High Rise Regular Jeans",59.90,"Jeans","blue","https://www.uniqlo.com/ca/en/products/E484037-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484037/item/cagoods_67_484037_3x4.jpg?width=300"),
    ("Cotton Culotte",59.90,"Pants","black","https://www.uniqlo.com/ca/en/products/E483042-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483042/item/cagoods_09_483042_3x4.jpg?width=300"),
    ("Linen Blend Easy Shorts",34.90,"Shorts","black","https://www.uniqlo.com/ca/en/products/E485251-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/485251/item/cagoods_69_485251_3x4.jpg?width=300"),
]:
    products.append({"name":name,"brand":"UNIQLO","cat":cat,"color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Uniqlo Outerwear
for name, price, cat, url, img in [
    ("Cotton Blend Short Blouson",79.90,"Jacket","https://www.uniqlo.com/ca/en/products/E484032-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484032/item/cagoods_72_484032_3x4.jpg?width=300"),
    ("Utility Short Coat",129.90,"Coat","https://www.uniqlo.com/ca/en/products/E483037-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483037/item/cagoods_58_483037_3x4.jpg?width=300"),
    ("Zip-Up Short Jacket",79.90,"Jacket","https://www.uniqlo.com/ca/en/products/E479208-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/479208/item/cagoods_69_479208_3x4.jpg?width=300"),
    ("Utility Short Jacket",79.90,"Jacket","https://www.uniqlo.com/ca/en/products/E483807-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483807/item/cagoods_33_483807_3x4.jpg?width=300"),
    ("Utility Denim Jacket",79.90,"Jacket","https://www.uniqlo.com/ca/en/products/E484664-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484664/item/cagoods_69_484664_3x4.jpg?width=300"),
    ("Soft Brushed Short Jacket",89.90,"Jacket","https://www.uniqlo.com/ca/en/products/E485706-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/485706/item/cagoods_37_485706_3x4.jpg?width=300"),
    ("Linen Blend Coverall",69.90,"Jacket","https://www.uniqlo.com/ca/en/products/E482273-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482273/item/cagoods_30_482273_3x4.jpg?width=300"),
    ("Pufftech Collarless Jacket",39.90,"Jacket","https://www.uniqlo.com/ca/en/products/E482274-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482274/item/cagoods_09_482274_3x4.jpg?width=300"),
    ("Tailored Jacket",59.90,"Jacket","https://www.uniqlo.com/ca/en/products/E483036-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483036/item/cagoods_39_483036_3x4.jpg?width=300"),
    ("Premium Linen Jacket",149.90,"Jacket","https://www.uniqlo.com/ca/en/products/E483762-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483762/item/cagoods_68_483762_3x4.jpg?width=300"),
    ("Double Breasted Jacket",99.90,"Jacket","https://www.uniqlo.com/ca/en/products/E478557-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/478557/item/cagoods_05_478557_3x4.jpg?width=300"),
    ("Cotton Blend Short Parka",79.90,"Coat","https://www.uniqlo.com/ca/en/products/E479229-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/479229/item/cagoods_31_479229_3x4.jpg?width=300"),
    ("Windproof Short Parka",49.90,"Coat","https://www.uniqlo.com/ca/en/products/E484022-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484022/item/cagoods_69_484022_3x4.jpg?width=300"),
    ("Pufftech Parka",99.90,"Coat","https://www.uniqlo.com/ca/en/products/E469871-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/469871/item/cagoods_09_469871_3x4.jpg?width=300"),
    ("UV Protection Parka",59.90,"Coat","https://www.uniqlo.com/ca/en/products/E485671-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/485671/item/cagoods_63_485671_3x4.jpg?width=300"),
    ("Fluffy Fleece Jacket",49.90,"Jacket","https://www.uniqlo.com/ca/en/products/E449753-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/449753/item/cagoods_36_449753_3x4.jpg?width=300"),
    ("Seamless Down Parka",159.90,"Coat","https://www.uniqlo.com/ca/en/products/E478577-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/478577/item/cagoods_09_478577_3x4.jpg?width=300"),
    ("Denim Relaxed Shirt Jacket",59.90,"Jacket","https://www.uniqlo.com/ca/en/products/E483767-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483767/item/cagoods_00_483767_3x4.jpg?width=300"),
]:
    products.append({"name":name,"brand":"UNIQLO","cat":cat,"color":"black","style":"casual","price":str(price),"image_url":img,"url":url})

# Uniqlo Dresses
for name, price, cat, url, img in [
    ("AIRism Cotton Camisole Dress",49.90,"Dress","https://www.uniqlo.com/ca/en/products/E482808-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482808/item/cagoods_09_482808_3x4.jpg?width=300"),
    ("Ribbed Bra Dress",59.90,"Dress","https://www.uniqlo.com/ca/en/products/E482802-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482802/item/cagoods_05_482802_3x4.jpg?width=300"),
    ("Extra Stretch AIRism Dress",49.90,"Dress","https://www.uniqlo.com/ca/en/products/E482982-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482982/item/cagoods_68_482982_3x4.jpg?width=300"),
    ("Linen Blend Mini Dress",59.90,"Dress","https://www.uniqlo.com/ca/en/products/E482795-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482795/item/cagoods_17_482795_3x4.jpg?width=300"),
    ("Linen Blend Tiered Dress",69.90,"Dress","https://www.uniqlo.com/ca/en/products/E482788-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482788/item/cagoods_15_482788_3x4.jpg?width=300"),
    ("Linen Blend V Neck Dress",79.90,"Dress","https://www.uniqlo.com/ca/en/products/E483823-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483823/item/cagoods_09_483823_3x4.jpg?width=300"),
    ("Cotton Volume Sleeve Dress",69.90,"Dress","https://www.uniqlo.com/ca/en/products/E483065-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483065/item/cagoods_69_483065_3x4.jpg?width=300"),
    ("3D Knit Cotton Dress",59.90,"Dress","https://www.uniqlo.com/ca/en/products/E484089-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484089/item/cagoods_35_484089_3x4.jpg?width=300"),
    ("Oversized T-Shirt Dress",29.90,"Dress","https://www.uniqlo.com/ca/en/products/E484003-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484003/item/cagoods_69_484003_3x4.jpg?width=300"),
    ("Oxford Shirt Dress",39.90,"Dress","https://www.uniqlo.com/ca/en/products/E483822-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483822/item/cagoods_30_483822_3x4.jpg?width=300"),
    ("AIRism Cotton Relaxed Dress",49.90,"Dress","https://www.uniqlo.com/ca/en/products/E484091-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484091/item/cagoods_50_484091_3x4.jpg?width=300"),
    ("Fit and Flare Dress",49.90,"Dress","https://www.uniqlo.com/ca/en/products/E483069-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483069/item/cagoods_32_483069_3x4.jpg?width=300"),
]:
    products.append({"name":name,"brand":"UNIQLO","cat":cat,"color":"black","style":"casual","price":str(price),"image_url":img,"url":url})

# Uniqlo Skirts
for name, price, url, img in [
    ("Slit Skort",49.90,"https://www.uniqlo.com/ca/en/products/E485473-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/485473/item/cagoods_09_485473_3x4.jpg?width=300"),
    ("Pleated Skort",49.90,"https://www.uniqlo.com/ca/en/products/E480302-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/480302/item/cagoods_31_480302_3x4.jpg?width=300"),
    ("Denim Mini Skirt",49.90,"https://www.uniqlo.com/ca/en/products/E485264-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/485264/item/cagoods_00_485264_3x4.jpg?width=300"),
    ("Tiered Maxi Skirt",59.90,"https://www.uniqlo.com/ca/en/products/E482286-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482286/item/cagoods_00_482286_3x4.jpg?width=300"),
    ("Linen Blend Tuck Long Skirt",59.90,"https://www.uniqlo.com/ca/en/products/E482285-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482285/item/cagoods_69_482285_3x4.jpg?width=300"),
    ("Mermaid Maxi Skirt",29.90,"https://www.uniqlo.com/ca/en/products/E484853-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484853/item/cagoods_09_484853_3x4.jpg?width=300"),
    ("Satin Long Skirt",39.90,"https://www.uniqlo.com/ca/en/products/E483045-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483045/item/cagoods_32_483045_3x4.jpg?width=300"),
]:
    products.append({"name":name,"brand":"UNIQLO","cat":"Skirt","color":"black","style":"casual","price":str(price),"image_url":img,"url":url})

# Zara T-shirts
for name, price, color, url, img in [
    ("Contrast Trim Bodysuit",29.90,"black","https://www.zara.com/ca/en/contrast-trim-bodysuit-p04424334.html","https://static.zara.net/assets/public/41ea/4a80/dff14c328a8c/a6a696aab84a/04424334076-p/04424334076-p.jpg?ts=1775052503791&w=1809"),
    ("Washed Effect T-Shirt",29.90,"red","https://www.zara.com/ca/en/washed-effect-text-t-shirt-p06145001.html","https://static.zara.net/assets/public/3b24/2ad2/d8974882bfe0/23084ad1904c/06145001600-a1/06145001600-a1.jpg?ts=1775052069934&w=1809"),
    ("Rustic Sleeveless T-Shirt",22.90,"beige","https://www.zara.com/ca/en/rustic-sleeveless-t-shirt-p04174046.html","https://static.zara.net/assets/public/fa71/df83/34b348ea95d5/a8f161730117/04174046718-p/04174046718-p.jpg?ts=1775065426074&w=1809"),
    ("Rustic Text T-Shirt",29.90,"white","https://www.zara.com/ca/en/rustic-text-t-shirt-p06145003.html","https://static.zara.net/assets/public/9c3b/602c/24114efa9093/2873d6e6674a/06145003251-a1/06145003251-a1.jpg?ts=1775052074764&w=1809"),
    ("Contrast Trim Text T-Shirt",29.90,"beige","https://www.zara.com/ca/en/contrast-trim-text-t-shirt-p06145002.html","https://static.zara.net/assets/public/ffc3/4919/3f3f42449de1/b93b61753cfc/06145002251-a1/06145002251-a1.jpg?ts=1775052074165&w=1809"),
    ("Contrast Embroidery T-Shirt",32.90,"white","https://www.zara.com/ca/en/contrast-embroidery-t-shirt-p03253013.html","https://static.zara.net/assets/public/73e0/3b7b/b470404abbf8/358224484e05/03253013251-a1/03253013251-a1.jpg?ts=1775482108211&w=1809"),
    ("Ruffled Sleeve T-Shirt",32.90,"white","https://www.zara.com/ca/en/ruffle-sleeve-t-shirt-p01165121.html","https://static.zara.net/assets/public/e5b1/ec18/ef1646c8a34c/6de1092091b0/01165121250-a1/01165121250-a1.jpg?ts=1775482101042&w=1809"),
    ("Rustic Short Sleeve T-Shirt",29.90,"purple","https://www.zara.com/ca/en/rustic-short-sleeve-t-shirt-p04174045.html","https://static.zara.net/assets/public/b967/a3a2/e6984efdacd6/3546a433895c/04174045669-p/04174045669-p.jpg?ts=1775027756737&w=1809"),
    ("Cotton Button T-Shirt",35.90,"white","https://www.zara.com/ca/en/100-cotton-button-t-shirt-p00858016.html","https://static.zara.net/assets/public/71e2/1bf0/13df4614aa0b/791073615f90/00858016250-a1/00858016250-a1.jpg?ts=1775047044662&w=1809"),
    ("Supima Three-Quarter Sleeve T-Shirt",32.90,"brown","https://www.zara.com/ca/en/supima--three-quarter-sleeve-t-shirt-p00264042.html","https://static.zara.net/assets/public/885e/3dcd/bf7046578de4/ac9f23c50a18/00264042643-p/00264042643-p.jpg?ts=1775047044449&w=1809"),
    ("Flame Text T-Shirt",32.90,"blue","https://www.zara.com/ca/en/flame-t-shirt-with-trims-p04424012.html","https://static.zara.net/assets/public/9e3d/630e/cb7b4289bb45/cd34a403a1d3/04424012407-p/04424012407-p.jpg?ts=1775052048967&w=1809"),
    ("Off-the-Shoulder T-Shirt",22.90,"black","https://www.zara.com/ca/en/off-the-shoulder-t-shirt-p02335179.html","https://static.zara.net/assets/public/fa9e/ec98/dcd946c18168/c46d4ec6350b/02335179800-a2/02335179800-a2.jpg?ts=1775062927622&w=1809"),
    ("Boat Neck Top",22.90,"white","https://www.zara.com/ca/en/boat-neck-top-p03641301.html","https://static.zara.net/assets/public/b216/121b/38f044f7aacf/966c2bd708f3/03641301250-p/03641301250-p.jpg?ts=1775027737264&w=1809"),
    ("Basic Rib T-Shirt",45.90,"white","https://www.zara.com/ca/en/basic-rib-knit-t-shirt-p08779123.html","https://static.zara.net/assets/public/57b8/69b3/b96b49a180fb/91fa220f28dc/08779123250-p/08779123250-p.jpg?ts=1775062009720&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"T-shirt","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Jeans
for name, price, url, img in [
    ("Mid-Rise Cropped Jeans",65.90,"https://www.zara.com/ca/en/z1975-mid-rise-cropped-jeans-p01934033.html","https://static.zara.net/assets/public/c4ab/c28c/71bf498aa091/2c852fb78bdb/a19429bddafb994fae4ec5dd2d8a1766/a19429bddafb994fae4ec5dd2d8a1766.jpg?ts=1775063735227&w=1809"),
    ("Relaxed Ankle Jeans",65.90,"https://www.zara.com/ca/en/zw-collection-mid-rise-relaxed-ankle-jeans-p08307045.html","https://static.zara.net/assets/public/7043/03c6/7e844cda8258/f34cefdc7ec3/2b0ca840da2387bfcf08e640f1e456c4/2b0ca840da2387bfcf08e640f1e456c4.jpg?ts=1775063077476&w=1809"),
    ("Cigarette Jeans",69.90,"https://www.zara.com/ca/en/zw-collection-mid-rise-cigarette-jeans-p04676244.html","https://static.zara.net/assets/public/e1f3/24c6/38b04827b2df/aef065ea7c1f/5c96765eb3aa5aa2efcae1f16327e8ff/5c96765eb3aa5aa2efcae1f16327e8ff.jpg?ts=1775466321992&w=1809"),
    ("Wide Leg High-Rise Jeans",65.90,"https://www.zara.com/ca/en/zw-collection-wide-leg-high-rise-jeans-p05474058.html","https://static.zara.net/assets/public/ebd9/e599/9c754da08ee3/ec027f32439c/140803e17b5a0a4390d11e3e46010e68/140803e17b5a0a4390d11e3e46010e68.jpg?ts=1775466317774&w=1809"),
    ("Low-Rise Crossed Jeans",69.90,"https://www.zara.com/ca/en/z1975-low-rise-crossed-jeans-p06147116.html","https://static.zara.net/assets/public/ca20/b720/b21a43dba3bc/f62af08f938e/271ec1944132310e88e4579c5dece9f2/271ec1944132310e88e4579c5dece9f2.jpg?ts=1775484882545&w=1809"),
    ("Tapered Mid-Rise Jeans",65.90,"https://www.zara.com/ca/en/zw-collection-tapered-mid-rise-jeans-p05474051.html","https://static.zara.net/assets/public/6489/e1f7/aca2435391ab/4d753cfc0379/1c5dc189c3d1e5f4ae9e3aa9044726a5/1c5dc189c3d1e5f4ae9e3aa9044726a5.jpg?ts=1775466320329&w=1809"),
    ("Ripped Straight Leg Jeans",69.90,"https://www.zara.com/ca/en/zw-collection-mid-rise-ripped-straight-leg-jeans-p06840101.html","https://static.zara.net/assets/public/75d7/670f/9d1441cfb18e/0ed40994f0f4/b47ead36aea7562e93fafde536184fcb/b47ead36aea7562e93fafde536184fcb.jpg?ts=1775063076915&w=1809"),
    ("High-Waist Wide Leg Jeans",65.90,"https://www.zara.com/ca/en/z1975-high-waist-straight-long-length-jeans-p08228021.html","https://static.zara.net/assets/public/3ad5/1ba0/99074789b1a7/e0d939aea7b4/08228021250-f1/08228021250-f1.jpg?ts=1770377401505&w=1769"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Jeans","color":"blue","style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Shoes
for name, price, color, cat, url, img in [
    ("Leather Heeled Sandals",219.00,"beige","Heels","https://www.zara.com/ca/en/leather-heeled-sandals---the-item-zara-woman-p11380710.html","https://static.zara.net/assets/public/8603/09df/9ac34ef9bdc7/7f5b71251a5f/9cbf3580dec594857dfb24cfe77892d9/9cbf3580dec594857dfb24cfe77892d9.jpg?ts=1775031392306&w=1809"),
    ("Knotted Flat Sandals",79.90,"brown","Flats","https://www.zara.com/ca/en/knotted-flat-sandals-p11648710.html","https://static.zara.net/assets/public/8160/c16c/04bf4a6883ce/a081e709bf05/01936334250-015-a2/01936334250-015-a2.jpg?ts=1775047840307&w=1809"),
    ("Strappy Heeled Sandals",65.90,"blue","Heels","https://www.zara.com/ca/en/strappy-heeled-sandals-p13384710.html","https://static.zara.net/assets/public/a260/3759/a4f44ce88fc5/9a7a305bc1a4/T9800833379-p/T9800833379-p.jpg?ts=1775071511396&w=1809"),
    ("Satin Effect Heeled Sandals",65.90,"pink","Heels","https://www.zara.com/ca/en/satin-effect-heeled-sandals-p13379710.html","https://static.zara.net/assets/public/fc3d/0325/95ef48278d84/2aa108a30339/05129046712-000-p/05129046712-000-p.jpg?ts=1775056895430&w=1809"),
    ("Flat Leather Sandals",65.90,"black","Flats","https://www.zara.com/ca/en/flat-leather-sandals-p11629710.html","https://static.zara.net/assets/public/7869/ed1a/1d8942a587d1/eeaa10b86770/02724337533-000-p/02724337533-000-p.jpg?ts=1775056141584&w=1809"),
    ("Running Sneakers",59.90,"green","Sneakers","https://www.zara.com/ca/en/running-sneakers-p15060710.html","https://static.zara.net/assets/public/a260/3759/a4f44ce88fc5/9a7a305bc1a4/T9800833379-p/T9800833379-p.jpg?ts=1775071511396&w=1809"),
    ("Braided Ballet Flats",79.90,"brown","Flats","https://www.zara.com/ca/en/braided-ballet-flats-p12532710.html","https://static.zara.net/assets/public/8160/c16c/04bf4a6883ce/a081e709bf05/01936334250-015-a2/01936334250-015-a2.jpg?ts=1775047840307&w=1809"),
    ("Leather Slingback Heels",79.90,"brown","Heels","https://www.zara.com/ca/en/leather-slingback-heels-p13221710.html","https://static.zara.net/assets/public/8160/c16c/04bf4a6883ce/a081e709bf05/01936334250-015-a2/01936334250-015-a2.jpg?ts=1775047840307&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":cat,"color":color,"style":"formal" if cat=="Heels" else "casual","price":str(price),"image_url":img,"url":url})

# Zara Dresses
for name, price, color, url, img in [
    ("Ruffled Mini Dress",65.90,"white","https://www.zara.com/ca/en/ruffled-mini-dress-p07521329.html","https://static.zara.net/assets/public/c971/600e/ac3341828cb3/b5a0e1ef42b5/07521329250-p/07521329250-p.jpg?ts=1775052086854"),
    ("Embroidered Strap Mini Dress",65.90,"black","https://www.zara.com/ca/en/embroidered-strappy-mini-dress-p07521300.html","https://static.zara.net/assets/public/7291/efe8/4126459a904f/298126a9c6f7/07521300800-p/07521300800-p.jpg?ts=1775065323513"),
    ("Satin Effect Batwing Dress",169.00,"brown","https://www.zara.com/ca/en/batwing-sleeve-slit-satin-effect-dress-p02678126.html","https://static.zara.net/assets/public/09b8/b8e6/30ee4297bcbb/b29fa7244c90/02678126615-a1/02678126615-a1.jpg?ts=1775058831468"),
    ("Combination Knit Dress",79.90,"black","https://www.zara.com/ca/en/combination-knit-dress-p09325001.html","https://static.zara.net/assets/public/cb5d/a3b3/06f44d82b955/d009e7af8ff7/09325001084-p/09325001084-p.jpg?ts=1775058877824"),
    ("Floral Print Dress",169.00,"red","https://www.zara.com/ca/en/zw-collection-floral-print-dress-p02111100.html","https://static.zara.net/assets/public/6ba6/74b7/ebdc41b4aaac/a0667fb70a7a/02111100094-a2/02111100094-a2.jpg?ts=1775058823503"),
    ("Belted Striped Halter Dress",45.90,"brown","https://www.zara.com/ca/en/striped-halter-dress-with-belt-p05063353.html","https://static.zara.net/assets/public/4c86/9bf6/8aa34b8cbdcb/a0169de02cc9/05063353178-h/05063353178-h.jpg?ts=1775052058429"),
    ("Halter Swing Dress",65.90,"yellow","https://www.zara.com/ca/en/swing-halter-dress-p02739111.html","https://static.zara.net/assets/public/a47b/f0d9/b6da416f9e7e/6121957c1693/02739111300-a1/02739111300-a1.jpg?ts=1775064957420"),
    ("Linen Blend Midi Dress",99.90,"pink","https://www.zara.com/ca/en/zw-collection-linen-blend-midi-dress-p05289025.html","https://static.zara.net/assets/public/4ef7/5219/c0804d28b420/e304594fe2d0/05289025620-a2/05289025620-a2.jpg?ts=1775059694704"),
    ("Beaded Knit Mini Dress",65.90,"black","https://www.zara.com/ca/en/beaded-slit-knit-short-dress-p03921018.html","https://static.zara.net/assets/public/e64b/c33e/ce6d4f4a8617/94fb687eb7f2/03921018800-a3/03921018800-a3.jpg?ts=1775062986394"),
    ("Polka Dot Short Dress",79.90,"white","https://www.zara.com/ca/en/polka-dot-short-dress-p03897114.html","https://static.zara.net/assets/public/7a10/8d70/fdf54144be38/15188c083573/03897114064-h1/03897114064-h1.jpg?ts=1775046640074"),
    ("Asymmetric Midi Dress",79.90,"black","https://www.zara.com/ca/en/asymmetric-midi-dress-p02359322.html","https://static.zara.net/assets/public/db3a/eb96/81274a0e8cfe/e95546ab6c61/02359322800-a2/02359322800-a2.jpg?ts=1775046636767"),
    ("Flowy Strappy Midi Dress",55.90,"red","https://www.zara.com/ca/en/flowy-strappy-midi-dress-p05039380.html","https://static.zara.net/assets/public/de73/3557/9a844fb28a52/ef592c047a7a/05039380600-p/05039380600-p.jpg?ts=1773249254825"),
    ("Lace Volume Dress",55.90,"gray","https://www.zara.com/ca/en/lace-voluminous-dress-p05584395.html","https://static.zara.net/assets/public/132f/9917/b9c84070a31f/341c684794c7/05584395485-a2/05584395485-a2.jpg?ts=1775061161043"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Dress","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Outerwear
for name, price, cat, url, img in [
    ("Faux Suede Jacket",89.90,"Jacket","https://www.zara.com/ca/en/faux-suede-jacket-p03046203.html","https://static.zara.net/assets/public/48a0/d7c0/3ebf47fb89a8/df89c9e408ff/03046203507-a1/03046203507-a1.jpg?ts=1770993803885&w=1809"),
    ("Faux Leather Jacket",139.00,"Jacket","https://www.zara.com/ca/en/faux-leather-jacket-p04391892.html","https://static.zara.net/assets/public/1ab2/2525/e79347469d55/6d8787a6603f/04341892700-a2/04341892700-a2.jpg?ts=1771940730323&w=1809"),
    ("Suede Leather Fitted Jacket",329.00,"Jacket","https://www.zara.com/ca/en/100-suede-leather-fitted-jacket-p04341826.html","https://static.zara.net/assets/public/3681/232f/362348dda7f4/a006f2c84d55/04341826506-a1/04341826506-a1.jpg?ts=1772618854105&w=1809"),
    ("Faux Leather Jacket with Belt",109.00,"Jacket","https://www.zara.com/ca/en/faux-leather-jacket-with-belt-p04341823.html","https://static.zara.net/assets/public/531e/0b0c/912a465ea7c7/32d9be9aa390/05854833800-p/05854833800-p.jpg?ts=1774618470179&w=1809"),
    ("Rustic Buttoned Blazer",75.90,"Jacket","https://www.zara.com/ca/en/rustic-buttoned-blazer-p02010716.html","https://static.zara.net/assets/public/d17b/0c2e/3bc543f3a842/f5ba1b4db0b9/02010716916-p/02010716916-p.jpg?ts=1774615906556&w=1809"),
    ("Cropped Denim Jacket",89.90,"Jacket","https://www.zara.com/ca/en/z1975-cropped-denim-jacket-p07147034.html","https://static.zara.net/assets/public/50af/b07f/294643e79a24/369df741e47a/07147034030-a3/07147034030-a3.jpg?ts=1773244958112&w=1809"),
    ("Denim Bomber Jacket",79.90,"Jacket","https://www.zara.com/ca/en/z1975-high-collar-denim-bomber-jacket-p04083033.html","https://static.zara.net/assets/public/0d13/4982/e2964f40a57a/4591c3d43fc3/04083033407-a1/04083033407-a1.jpg?ts=1773411800420&w=1809"),
    ("Fitted Linen Jacket",99.90,"Jacket","https://www.zara.com/ca/en/fitted-linen-jacket-with-shoulder-pads-p02572998.html","https://static.zara.net/assets/public/b474/f306/587b4a309d00/d6398a9858f3/02572998052-p/02572998052-p.jpg?ts=1774622162640&w=1809"),
    ("Denim Jacket",55.90,"Jacket","https://www.zara.com/ca/en/z1975-denim-jacket-p00108022.html","https://static.zara.net/assets/public/3f5a/f495/06324270b2a9/c3dc4beedcdb/00108022700-p/00108022700-p.jpg?ts=1773253597070&w=1809"),
    ("Washed Effect Trench Coat",75.90,"Coat","https://www.zara.com/ca/en/washed-effect-short-trench-coat-p02634787.html","https://static.zara.net/assets/public/9aaa/d810/5ff7469fa552/927e553915e8/02634787704-p/02634787704-p.jpg?ts=1774015564797&w=1809"),
    ("Balloon Jacket",79.90,"Jacket","https://www.zara.com/ca/en/balloon-jacket-p03046043.html","https://static.zara.net/assets/public/c2c4/9c30/b9014c5a8b68/a9f79b1445dd/03046043704-a1/03046043704-a1.jpg?ts=1774450604219&w=1809"),
    ("Pocket Blazer",139.00,"Jacket","https://www.zara.com/ca/en/zw-collection-pocket-blazer-p02712464.html","https://static.zara.net/assets/public/a5d9/3f24/f17b4a05bbde/e028a983a167/02712464800-p/02712464800-p.jpg?ts=1774014856266&w=1809"),
    ("Cropped Faux Suede Jacket",75.90,"Jacket","https://www.zara.com/ca/en/cropped-faux-suede-jacket-p03046033.html","https://static.zara.net/assets/public/3340/9cf7/0ee44040afab/f3a45feb0bfd/08073063507-p/08073063507-p.jpg?ts=1771417935270&w=1809"),
    ("Bomber Jacket",59.90,"Jacket","https://www.zara.com/ca/en/high-collar-bomber-jacket-p08372027.html","https://static.zara.net/assets/public/8f20/dabf/b78648e6865e/f92a475bbc0f/08372027712-a5/08372027712-a5.jpg?ts=1771263285130&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":cat,"color":"black","style":"casual" if "denim" in name.lower() else "formal","price":str(price),"image_url":img,"url":url})

# Zara Skirts
for name, price, color, url, img in [
    ("Lace Pareo Skirt",89.90,"beige","https://www.zara.com/ca/en/zw-collection-lace-pareo-skirt-p04786145.html","https://static.zara.net/assets/public/4c8f/6289/34224fbdbb59/12b8f0151b7a/04786145251-a4/04786145251-a4.jpg?ts=1775058851079&w=1809"),
    ("Satin Effect Lace Skirt",79.90,"white","https://www.zara.com/ca/en/zw-collection-satin-lace-skirt-p02731054.html","https://static.zara.net/assets/public/6340/8f1a/0a7e45428732/6184fe55a704/02731054727-a1/02731054727-a1.jpg?ts=1775058842186&w=1809"),
    ("Embroidered Belt Midi Skirt",99.90,"beige","https://www.zara.com/ca/en/embroidered-belt-midi-skirt-zw-collection-p05358040.html","https://static.zara.net/assets/public/862b/77c5/fd9342ec8276/4a52321e8b04/05358040712-p/05358040712-p.jpg?ts=1775049259559&w=1809"),
    ("Textured Midi Skirt",35.90,"black","https://www.zara.com/ca/en/textured-midi-skirt-p05039391.html","https://static.zara.net/assets/public/7964/2e3e/8a6d448f99ff/22e4c792a1c6/05039391800-a1/05039391800-a1.jpg?ts=1775060782305&w=1809"),
    ("Stretch Lace Mini Skirt",35.90,"black","https://www.zara.com/ca/en/stretch-lace-mini-skirt-p05584449.html","https://static.zara.net/assets/public/ae8f/dc71/57f449b7bbb1/74d92cd71c7b/05584449800-p/05584449800-p.jpg?ts=1775055818693&w=1809"),
    ("Asymmetric Hem Mini Skirt",65.90,"green","https://www.zara.com/ca/en/zw-collection-asymmetric-hem-mini-skirt-p02570199.html","https://static.zara.net/assets/public/0a20/4a62/ccea4069b548/fc151ae929b7/02570199500-p/02570199500-p.jpg?ts=1775047043660&w=1809"),
    ("Asymmetric Skort",55.90,"black","https://www.zara.com/ca/en/asymmetric-skort-with-applique-p01971241.html","https://static.zara.net/assets/public/efcb/7bf2/395d4c7db94e/dfbba43e4d52/01971241800-a1/01971241800-a1.jpg?ts=1775046636397&w=1809"),
    ("Puffed Midi Skirt",65.90,"red","https://www.zara.com/ca/en/puffed-midi-skirt-p05029051.html","https://static.zara.net/assets/public/ea55/48a0/ab1e4212b118/5999329e0335/05029051606-000-e1/05029051606-000-e1.jpg?ts=1772099174590&w=1809"),
    ("Lace Midi Skirt",65.90,"blue","https://www.zara.com/ca/en/lace-midi-skirt-p08741102.html","https://static.zara.net/assets/public/a985/57c9/992c4a4390e7/91827e733f22/08741102423-p/08741102423-p.jpg?ts=1774884882953&w=1809"),
    ("Polka Dot Satin Midi Skirt",45.90,"black","https://www.zara.com/ca/en/satin-effect-midi-skirt-p08338537.html","https://static.zara.net/assets/public/2b43/8448/eae84c5f82f6/913f6091da05/08338404070-p/08338404070-p.jpg?ts=1774970886875&w=1809"),
    ("Wrap Midi Skirt",55.90,"pink","https://www.zara.com/ca/en/wrap-midi-skirt-p04391446.html","https://static.zara.net/assets/public/a101/2101/5f8147e3a34c/b0ec3eb6446d/04391446644-p/04391446644-p.jpg?ts=1774371058466&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Skirt","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Pants
for name, price, color, url, img in [
    ("Wide-Leg Linen Pants",69.90,"brown","https://www.zara.com/ca/en/wide-leg-linen-pants-p02574771.html","https://static.zara.net/assets/public/57b1/5215/f8d647d5b622/e3a59656385e/02574771700-p/02574771700-p.jpg?ts=1775062960402&w=1809"),
    ("Flowy Wide Leg Pants",45.90,"pink","https://www.zara.com/ca/en/flowy-wide-leg-pants-p09929249.html","https://static.zara.net/assets/public/8604/1197/7e0b4d22b100/bc6c139c141f/09929249620-a1/09929249620-a1.jpg?ts=1775063023375&w=1809"),
    ("Linen Straight Leg Pants",59.90,"beige","https://www.zara.com/ca/en/linen-straight-leg-pants-p09929141.html","https://static.zara.net/assets/public/be58/fc99/c1d640de9c43/0668ceb85987/09929141052-p/09929141052-p.jpg?ts=1775064549192&w=1809"),
    ("Pleated Culottes",65.90,"blue","https://www.zara.com/ca/en/pleated-culottes-p02711841.html","https://static.zara.net/assets/public/03be/20ca/f69b468ba4db/1c8923b05b75/02711841400-e1/02711841400-e1.jpg?ts=1775041775740&w=1809"),
    ("Polka Dot High-Waisted Pants",55.90,"black","https://www.zara.com/ca/en/high-waisted-polka-dot-pants-p01478931.html","https://static.zara.net/assets/public/f64f/bc11/2ffe48ef9e18/a2048915ae4b/01478931064-p/01478931064-p.jpg?ts=1775042798752&w=1809"),
    ("Straight Chino Pants",69.90,"beige","https://www.zara.com/ca/en/zw-collection-straight-chino-pants-p05344045.html","https://static.zara.net/assets/public/8dba/ba53/63f54eee824a/530c21a43082/05344045712-p/05344045712-p.jpg?ts=1775058855391&w=1809"),
    ("Linen Blend Pants",79.90,"beige","https://www.zara.com/ca/en/zw-collection-linen-blend-pants-p04344042.html","https://static.zara.net/assets/public/f514/2111/2cdd44b6911c/c01708840f38/T9419883763-p/T9419883763-p.jpg?ts=1775051701492&w=1809"),
    ("Wide Leg Scarf Print Pants",65.90,"gray","https://www.zara.com/ca/en/wide-leg-pants-with-scarf-print-p07484022.html","https://static.zara.net/assets/public/14a0/55a1/81244ceb8bc2/ce388992d6cd/07484022086-a1/07484022086-a1.jpg?ts=1775063532281&w=1809"),
    ("Flowy Palazzo Pants",45.90,"beige","https://www.zara.com/ca/en/flowy-palazzo-pants-p05427434.html","https://static.zara.net/assets/public/2e24/60aa/1d1b4bdf994f/46c45dc4ef61/05427434806-p/05427434806-p.jpg?ts=1775052069474&w=1809"),
    ("Textured Straight Leg Pants",39.90,"beige","https://www.zara.com/ca/en/textured-straight-leg-pants-p05039396.html","https://static.zara.net/assets/public/0dd6/df82/d15f4df682ef/fefb74765b2d/05039396712-p/05039396712-p.jpg?ts=1775060204656&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Pants","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Shirts/Blouses (Round 2)
for name, price, color, url, img in [
    ("Oversized Gauze Shirt with Pocket",39.90,"blue","https://www.zara.com/ca/en/oversized-gauze-shirt-with-pocket-p07521001.html","https://static.zara.net/assets/public/83b9/4d79/57fc44fda6c9/c2b2270efd91/07521003080-a2/07521003080-a2.jpg?ts=1775052504182&w=1809"),
    ("Striped Poplin Shirt with Pleats",55.90,"blue","https://www.zara.com/ca/en/striped-poplin-shirt-with-pleats-p02110891.html","https://static.zara.net/assets/public/dcca/a2fc/40e3438ca34f/aefe4a393ff6/02110891944-p/02110891944-p.jpg?ts=1775042808306&w=1809"),
    ("Embroidered Eyelet Short Sleeve Shirt",65.90,"white","https://www.zara.com/ca/en/short-sleeve-embroidered-eyelet-shirt-p08372104.html","https://static.zara.net/assets/public/74d3/8b6d/6cf4402b9f5f/4fd87b5e6c15/08372104330-e1/08372104330-e1.jpg?ts=1775055549067&w=1809"),
    ("Ruffled Wrap Top",45.90,"pink","https://www.zara.com/ca/en/ruffled-wrap-top-p07521070.html","https://static.zara.net/assets/public/3808/aaac/df324f2cb11a/c31e4ba23a07/07521070620-p/07521070620-p.jpg?ts=1775064979397&w=1809"),
    ("ZW Collection Flowy Shirt",65.90,"white","https://www.zara.com/ca/en/zw-collection-flowy-shirt-p04786151.html","https://static.zara.net/assets/public/8522/8e95/8a014a6b940e/49fcdf2bebb8/04786151251-a1/04786151251-a1.jpg?ts=1775059456621&w=1809"),
    ("Ruffled Poplin Shirt",45.90,"white","https://www.zara.com/ca/en/ruffled-poplin-shirt-p04772014.html","https://static.zara.net/assets/public/247a/4e93/e1fc4f3ab315/f81ca8dc00e0/04772013250-p/04772013250-p.jpg?ts=1775062252018&w=1809"),
    ("Romantic Embroidered Eyelet Blouse",59.90,"blue","https://www.zara.com/ca/en/romantic-embroidered-eyelet-blouse-p04387025.html","https://static.zara.net/assets/public/cd7d/ae59/cd8a49ec9757/390170025293/04387025044-a1/04387025044-a1.jpg?ts=1775482109714&w=1809"),
    ("Fluid Linen Shirt",45.90,"pink","https://www.zara.com/ca/en/fluid-linen-shirt-p02082813.html","https://static.zara.net/assets/public/0f8c/05c1/8b494e3f90d6/5b10249eba25/02082623046-a1/02082623046-a1.jpg?ts=1774953309846&w=1809"),
    ("Linen Blend Shirt with Puffed Hem",55.90,"white","https://www.zara.com/ca/en/linen-blend-shirt-with-puffed-hem-p03115734.html","https://static.zara.net/assets/public/4097/2205/0d414fb2a651/3d2b0432c9f7/03115734250-p/03115734250-p.jpg?ts=1774953309166&w=1809"),
    ("Ruffled Ladder Trim Blouse",45.90,"brown","https://www.zara.com/ca/en/ruffled-lace-blouse-p08741074.html","https://static.zara.net/assets/public/9d1b/03b8/7e964644b4f5/0277a9c90967/08741074700-f1/08741074700-f1.jpg?ts=1773060174693&w=1769"),
    ("Oversized Tie Shirt",55.90,"pink","https://www.zara.com/ca/en/oversized-tie-shirt-p02484268.html","https://static.zara.net/assets/public/a3f4/8733/63fa4f95a2c5/129e367e4147/02484268633-p/02484268633-p.jpg?ts=1775055815038&w=1809"),
    ("Embroidered Blouse",45.90,"white","https://www.zara.com/ca/en/embroidered-blouse-p08741022.html","https://static.zara.net/assets/public/9056/f0b9/5da44efdb31c/ac7d98f56530/08741022250-000-f1/08741022250-000-f1.jpg?ts=1772009957363&w=1769"),
    ("Satin Effect Shirt",45.90,"black","https://www.zara.com/ca/en/satin-effect-shirt-p04764004.html","https://static.zara.net/assets/public/745f/222d/7bb3418f9b0a/2af58392b1ae/07521001700-p/07521001700-p.jpg?ts=1775065426741&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Shirt","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Knitwear/Sweaters (Round 2)
for name, price, color, cat, url, img in [
    ("Combination Knit Top",45.90,"green","Sweater","https://www.zara.com/ca/en/combined-knit-top-p03921011.html","https://static.zara.net/assets/public/4c98/bd42/79b24a18bbdf/daa71ca24276/03921011505-a1/03921011505-a1.jpg?ts=1775062977661&w=1809"),
    ("Oversized Knit Top",55.90,"red","Sweater","https://www.zara.com/ca/en/oversized-knit-top-p02142246.html","https://static.zara.net/assets/public/0161/7f60/82434fde8693/76e085e75f9c/02142246600-a1/02142246600-a1.jpg?ts=1774619597198&w=1809"),
    ("Ruffled Knit Top",39.90,"pink","Sweater","https://www.zara.com/ca/en/ruffled-knit-top-p03456010.html","https://static.zara.net/assets/public/8d1f/ea13/8ede40cda357/bc4aae0e031d/03456010622-a2/03456010622-a2.jpg?ts=1775062976822&w=1809"),
    ("Round Neck Knit Sweater",65.90,"white","Sweater","https://www.zara.com/ca/en/round-neck-knit-sweater-p02142123.html","https://static.zara.net/assets/public/517e/292e/c9ae43608ab0/0924bc2fb029/02142123250-a1/02142123250-a1.jpg?ts=1775064539027&w=1809"),
    ("Knit Wrap Top",45.90,"black","Sweater","https://www.zara.com/ca/en/knit-wrap-top-p08779008.html","https://static.zara.net/assets/public/c794/9fd6/cd64493c9314/5202c5766da5/08779008800-ult2/08779008800-ult2.jpg?ts=1775058873216&w=1809"),
    ("Short Sleeve Cardigan",45.90,"brown","Sweater","https://www.zara.com/ca/en/short-sleeve-cardigan-p02142140.html","https://static.zara.net/assets/public/8ef3/0120/154540939e3e/f51b03549006/02142140617-a1/02142140617-a1.jpg?ts=1775058826496&w=1809"),
    ("Chunky Knit Cardigan",65.90,"purple","Sweater","https://www.zara.com/ca/en/chunky-knit-cardigan-p02142251.html","https://static.zara.net/assets/public/c89a/b9cc/8f704fc09ad6/bcff92f767b1/02142251629-p/02142251629-p.jpg?ts=1774529263947&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":cat,"color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Shoes (Round 2 - additional)
for name, price, color, cat, url, img in [
    ("Metallic Knotted Heeled Sandals",69.90,"beige","Heels","https://www.zara.com/ca/en/metallic-knotted-heeled-sandals-p11307710.html","https://static.zara.net/assets/public/a62c/e918/f7ec4abab59a/5f2732827a5d/T9152036859-p/T9152036859-p.jpg?ts=1775055566496&w=1809"),
    ("Metallic Flat Fisherman Sandals",65.90,"beige","Flats","https://www.zara.com/ca/en/metallic-effect-flat-fisherman-sandals-p11652710.html","https://static.zara.net/assets/public/ac83/4068/802b4b62a07f/db7dd69a5766/05129047658-000-p/05129047658-000-p.jpg?ts=1775056379365&w=1809"),
    ("Flat Leather Sandals Red",69.90,"red","Flats","https://www.zara.com/ca/en/flat-leather-sandals-p11616710.html","https://static.zara.net/assets/public/a8d3/14e6/a4954c9b8e8c/3d9ea0554792/04088046406-p/04088046406-p.jpg?ts=1775055409098&w=1809"),
    ("Sparkly Strap Sandals",79.90,"beige","Heels","https://www.zara.com/ca/en/sparkly-strap-sandals-p12820710.html","https://static.zara.net/assets/public/a041/6c6b/1b51420eabc9/de3a5b5d9b63/12820710098-ult39/12820710098-ult39.jpg?ts=1772723563656&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":cat,"color":color,"style":"formal" if cat=="Heels" else "casual","price":str(price),"image_url":img,"url":url})

# Zara Sweatshirts/Hoodies
for name, price, color, cat, url, img in [
    ("Text Sweatshirt",35.90,"gray","Hoodie","https://www.zara.com/ca/en/text-sweatshirt-p03253019.html","https://static.zara.net/assets/public/b7a1/5898/b32548fc882d/2b45ae806539/03253019822-p/03253019822-p.jpg?ts=1775027737343&w=1809"),
    ("ZA Zip Sweatshirt",59.90,"pink","Hoodie","https://www.zara.com/ca/en/za-zip-sweatshirt-p05644060.html","https://static.zara.net/assets/public/1e91/7817/71774d05a9a9/ed2a59a74e5e/05644060625-a1/05644060625-a1.jpg?ts=1775063499164&w=1809"),
    ("Oversized Zip-Up Sweatshirt",55.90,"red","Hoodie","https://www.zara.com/ca/en/oversized-zip-up-sweatshirt-p03641393.html","https://static.zara.net/assets/public/3247/843b/8e874df4aefe/134902801c69/03641393600-a2/03641393600-a2.jpg?ts=1774544790288&w=1809"),
    ("Printed Sweatshirt",65.90,"pink","Hoodie","https://www.zara.com/ca/en/washed-effect-printed-sweatshirt-agustina-shuan-p00085065.html","https://static.zara.net/assets/public/fe73/15e2/1cc84872b211/ec40fb71f1be/00085065620-p/00085065620-p.jpg?ts=1774452744834&w=1809"),
    ("Embossed Bow Sweatshirt",55.90,"brown","Hoodie","https://www.zara.com/ca/en/raised-bow-sweatshirt-p04805100.html","https://static.zara.net/assets/public/84a0/493c/59dc4d62ae59/1e950ff5296a/04805100700-f1/04805100700-f1.jpg?ts=1769432262255&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":cat,"color":color,"style":"sporty","price":str(price),"image_url":img,"url":url})

# Roots Boots
for name, price, color, url, img in [
    ("TUFF Boot",258.00,"black","https://www.roots.com/ca/en/tuff-boot-47010159.html","https://www.roots.com/dw/image/v2/BGGS_PRD/on/demandware.static/-/Sites-roots_master_catalog/default/dw56bef8db/images/47010159_Y20_a.jpg?sw=598&sh=840&sm=fit"),
    ("Junction Boot",228.00,"black","https://www.roots.com/ca/en/junction-boot-47010161.html","https://www.roots.com/dw/image/v2/BGGS_PRD/on/demandware.static/-/Sites-roots_master_catalog/default/dw28b35780/images/47010161_001_a.jpg?sw=598&sh=840&sm=fit"),
    ("Puff Boot",348.00,"black","https://www.roots.com/ca/en/puff-boot-47010163.html","https://www.roots.com/dw/image/v2/BGGS_PRD/on/demandware.static/-/Sites-roots_master_catalog/default/dw17b2ed3c/images/47010163_23F_a.jpg?sw=598&sh=840&sm=fit"),
    ("Nordic Shoe",278.00,"white","https://www.roots.com/ca/en/nordic-shoe-47010165.html","https://www.roots.com/dw/image/v2/BGGS_PRD/on/demandware.static/-/Sites-roots_master_catalog/default/dw5d015b22/images/47010165_010_a.jpg?sw=598&sh=840&sm=fit"),
    ("Junction Boot Brown",228.00,"brown","https://www.roots.com/ca/en/junction-boot-47010161.html?dwvar_47010161_color=Y20","https://www.roots.com/dw/image/v2/BGGS_PRD/on/demandware.static/-/Sites-roots_master_catalog/default/dw98fbdc73/images/47010161_Y20_a.jpg?sw=598&sh=840&sm=fit"),
    ("Nordic Boot",328.00,"white","https://www.roots.com/ca/en/nordic-boot-47010167.html","https://www.roots.com/dw/image/v2/BGGS_PRD/on/demandware.static/-/Sites-roots_master_catalog/default/dwb3cf771e/images/47010167_010_a.jpg?sw=598&sh=840&sm=fit"),
    ("TUFF Boot White",258.00,"white","https://www.roots.com/ca/en/tuff-boot-47010160.html","https://www.roots.com/dw/image/v2/BGGS_PRD/on/demandware.static/-/Sites-roots_master_catalog/default/dw202f23a2/images/47010160_010_a.jpg?sw=598&sh=840&sm=fit"),
    ("Nordic Shoe Black",278.00,"black","https://www.roots.com/ca/en/nordic-shoe-47010164.html","https://www.roots.com/dw/image/v2/BGGS_PRD/on/demandware.static/-/Sites-roots_master_catalog/default/dwd388a1f5/images/47010164_001_a.jpg?sw=598&sh=840&sm=fit"),
]:
    products.append({"name":name,"brand":"Roots","cat":"Boots","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Oak+Fort Sweatshirts
for name, price, color, url, img in [
    ("Fleece Studio Off Shoulder Sweatshirt",68.00,"gray","https://oakandfort.com/products/fleece-studio-off-shoulder-bubble-hem-sweatshirt-kt-15110-w","https://oakandfort.com/cdn/shop/files/TShirt-15110_Medium_Heather_Grey-1.jpg?v=1765328829&width=720"),
    ("Fleece Studio Crewneck Sweatshirt",58.00,"navy","https://oakandfort.com/products/fleece-studio-crewneck-sweatshirt-kt-14719-w","https://oakandfort.com/cdn/shop/files/TShirt-14719_Navy_Blue-1.jpg?v=1768600019&width=720"),
    ("Oversized Graphic Sweatshirt",33.60,"green","https://oakandfort.com/products/oversized-graphic-sweatshirt-kt-7515-m","https://oakandfort.com/cdn/shop/files/TShirt-7515_Deep_Green_W-8.jpg?v=1775510409&width=720"),
]:
    products.append({"name":name,"brand":"Oak+Fort","cat":"Hoodie","color":color,"style":"sporty","price":str(price),"image_url":img,"url":url})

# ══════════════════════════════════════════════════════════════
# Round 3 — Additional scraping (2026-04-11)
# ══════════════════════════════════════════════════════════════

# H&M Sneakers (Round 3)
for name, price, color, url, img in [
    ("Retro Sneakers Gray",49.99,"gray","https://www2.hm.com/en_ca/productpage.1273075012.html","https://image.hm.com/assets/hm/46/2c/462cd953cc286c0bb269bb96991cdb692f90ff93.jpg?imwidth=1536"),
    ("Chunky Sneakers White",59.99,"white","https://www2.hm.com/en_ca/productpage.1208972001.html","https://image.hm.com/assets/hm/e0/ef/e0ef2d2884c209c92c6ef74a85a0c3d73a3a1d47.jpg?imwidth=1536"),
    ("Retro Sneakers Beige",49.99,"beige","https://www2.hm.com/en_ca/productpage.1273075011.html","https://image.hm.com/assets/hm/f8/1a/f81a609864080ec0de4ad0aa5f97ba777aaf4033.jpg?imwidth=1536"),
    ("Retro Sneakers Red",49.99,"red","https://www2.hm.com/en_ca/productpage.1273075007.html","https://image.hm.com/assets/hm/5c/d2/5cd28882aec8b81cf1235c15ddd74e3abe189533.jpg?imwidth=1536"),
    ("Leather Sneakers Brown",129.00,"brown","https://www2.hm.com/en_ca/productpage.1319011002.html","https://image.hm.com/assets/hm/8c/88/8c8834085b6f2ee288a21e6bac9cd447f102ad91.jpg?imwidth=1536"),
    ("Twill Sneakers Beige",44.99,"beige","https://www2.hm.com/en_ca/productpage.1319863001.html","https://image.hm.com/assets/hm/bd/5b/bd5becb35006aa7d014f00e91cf9c815ada071c3.jpg?imwidth=1536"),
    ("Retro Sneakers Brown",49.99,"brown","https://www2.hm.com/en_ca/productpage.1273075013.html","https://image.hm.com/assets/hm/9a/5a/9a5ae37cb2948c30a9ef14b41395f60a956ac99d.jpg?imwidth=1536"),
    ("Twill Sneakers White",44.99,"white","https://www2.hm.com/en_ca/productpage.1319863002.html","https://image.hm.com/assets/hm/4c/1b/4c1b56bb2822f110036b7c4415b1f85fd03bd791.jpg?imwidth=1536"),
    ("Platform Sneakers Beige",49.99,"beige","https://www2.hm.com/en_ca/productpage.1312674001.html","https://image.hm.com/assets/hm/2d/41/2d41aeb7596b09b772e4c78ee6f0d7d97253da1a.jpg?imwidth=1536"),
    ("Chunky Sneakers Pink",59.99,"pink","https://www2.hm.com/en_ca/productpage.1208972010.html","https://image.hm.com/assets/hm/72/e7/72e7694a15fbf5d29a98186fd31069b6137145a4.jpg?imwidth=1536"),
    ("Retro Sneakers Yellow",49.99,"yellow","https://www2.hm.com/en_ca/productpage.1273075010.html","https://image.hm.com/assets/hm/f2/d1/f2d18821423d5f548ce36fe63f53a0951ca76825.jpg?imwidth=1536"),
    ("Platform Sneakers Beige",49.99,"beige","https://www2.hm.com/en_ca/productpage.1312674002.html","https://image.hm.com/assets/hm/cf/8c/cf8c0ac9b526da66157436046ef53a7c673413f0.jpg?imwidth=1536"),
    ("Suede Sneakers Beige",99.00,"beige","https://www2.hm.com/en_ca/productpage.1324858001.html","https://image.hm.com/assets/hm/68/68/6868fe871435e244d676ca269739046c7da70780.jpg?imwidth=1536"),
    ("Low-Top Sneakers Blue",59.99,"blue","https://www2.hm.com/en_ca/productpage.1268920008.html","https://image.hm.com/assets/hm/12/85/1285610f6420d5f4b3e5b54cc9feb58ad671597a.jpg?imwidth=1536"),
    ("Mesh High Tops Beige",59.99,"beige","https://www2.hm.com/en_ca/productpage.1312676001.html","https://image.hm.com/assets/hm/1b/04/1b0451fbbaa55004cd4d4bfa17dc6c131393add5.jpg?imwidth=1536"),
    ("Crochet-Look Sneakers Red",59.99,"red","https://www2.hm.com/en_ca/productpage.1319862001.html","https://image.hm.com/assets/hm/8c/9b/8c9b32f50b2d3fd0e1af8a4dbe2f81f0744765d2.jpg?imwidth=1536"),
    ("Low-Top Sneakers Red",59.99,"red","https://www2.hm.com/en_ca/productpage.1268920009.html","https://image.hm.com/assets/hm/bd/81/bd81c9d57680ce91f9dacb6fdebe8b9bcbf7cb78.jpg?imwidth=1536"),
    ("Leather Sneakers Beige",129.00,"beige","https://www2.hm.com/en_ca/productpage.1319011001.html","https://image.hm.com/assets/hm/8c/1c/8c1c532a249f3d151ae4db0666fd741791150817.jpg?imwidth=1536"),
    ("Canvas Sneakers White",44.99,"white","https://www2.hm.com/en_ca/productpage.1290585001.html","https://image.hm.com/assets/hm/6f/2b/6f2bfde24e567430dfc0b0aa4b348f649abc3a9b.jpg?imwidth=1536"),
    ("Suede Sneakers Brown",99.00,"brown","https://www2.hm.com/en_ca/productpage.1312658001.html","https://image.hm.com/assets/hm/3c/60/3c60c7bb648a61d3d5389df64ffb6c36443a9055.jpg?imwidth=1536"),
    ("Retro Sneakers Burgundy",49.99,"red","https://www2.hm.com/en_ca/productpage.1273075009.html","https://image.hm.com/assets/hm/67/76/6776c7661e60ca9282bc81b17c23be7d6a7f7db6.jpg?imwidth=1536"),
    ("Premium Sneakers White",129.00,"white","https://www2.hm.com/en_ca/productpage.1324713001.html","https://image.hm.com/assets/hm/30/10/30106bf3d7dd61da079ab56007278ecf0c9b90e6.jpg?imwidth=1536"),
    ("Classic Sneakers White",44.99,"white","https://www2.hm.com/en_ca/productpage.1208965001.html","https://image.hm.com/assets/hm/b5/5b/b55befe5d14745e38419c28f070382d95b01d472.jpg?imwidth=1536"),
    ("Classic Sneakers Beige",44.99,"beige","https://www2.hm.com/en_ca/productpage.1208965027.html","https://image.hm.com/assets/hm/26/5f/265fc80678dc97d53d6b431b097aa5b23d85261e.jpg?imwidth=1536"),
    ("Premium Sneakers Black",129.00,"black","https://www2.hm.com/en_ca/productpage.1324701001.html","https://image.hm.com/assets/hm/91/70/917070e54603ec688b53966b819c962f913f6bd2.jpg?imwidth=1536"),
    ("Chunky Sneakers Brown",59.99,"brown","https://www2.hm.com/en_ca/productpage.1208972009.html","https://image.hm.com/assets/hm/a4/24/a424a5a052f4a7567b6e73de962fb94ad6d8dde8.jpg?imwidth=1536"),
]:
    products.append({"name":name,"brand":"H&M","cat":"Sneakers","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Shorts (Round 3)
for name, price, color, url, img in [
    ("Z1975 Mom Fit Shorts",45.90,"blue","https://www.zara.com/ca/en/z1975-mom-fit-shorts-p07223038.html","https://static.zara.net/assets/public/b09e/4e0c/3fd04e5c8662/a87af0c8a0aa/07223038427-p/07223038427-p.jpg?ts=1775645647371&w=1849"),
    ("Sequin Lace Shorts",55.90,"white","https://www.zara.com/ca/en/sequined-lace-shorts-p04813330.html","https://static.zara.net/assets/public/b0d2/1b97/88e44e289e2b/19c9a90a79e4/04813330250-a1/04813330250-a1.jpg?ts=1775572242019&w=1849"),
    ("TRF Low-Rise Denim Mini Shorts",39.90,"blue","https://www.zara.com/ca/en/trf-low-rise-denim-mini-shorts-p04365003.html","https://static.zara.net/assets/public/d5cb/421d/3c8e408aa2c9/303212f5c4a4/00699001407-e1/00699001407-e1.jpg?ts=1775486490485&w=1849"),
    ("TRF Ripped High-Waisted Shorts",45.90,"black","https://www.zara.com/ca/en/trf-ripped-high-waisted-denim-shorts-p04365001.html","https://static.zara.net/assets/public/d277/5499/96824ee284ac/6fedfc2b0b9f/05252002800-p/05252002800-p.jpg?ts=1775680853818&w=1849"),
    ("ZW Collection Linen Shorts",65.90,"pink","https://www.zara.com/ca/en/zw-collection-linen-shorts-p04344040.html","https://static.zara.net/assets/public/824a/c36d/1c704029ae6f/0eecc90dd7a0/04344040619-a1/04344040619-a1.jpg?ts=1774949046384&w=1849"),
    ("Embroidered Shorts",69.90,"beige","https://www.zara.com/ca/en/embroidered-shorts-p05770025.html","https://static.zara.net/assets/public/1c0b/3c3b/ece242839a20/54701af3a80c/05770024712-p/05770024712-p.jpg?ts=1772636268104&w=1849"),
    ("Satin Effect Lace Mini Shorts",39.90,"beige","https://www.zara.com/ca/en/satin-effect-lace-mini-shorts-p01255427.html","https://static.zara.net/assets/public/3294/2024/9c8b4b6a9333/2fbd080ad2ca/05919124500-p/05919124500-p.jpg?ts=1774003342691&w=1849"),
    ("Mini Striped Shorts",39.90,"pink","https://www.zara.com/ca/en/mini-striped-shorts-p05063858.html","https://static.zara.net/assets/public/f748/678e/b7d34e2b8e66/99ce8ed8907e/05063858620-p/05063858620-p.jpg?ts=1775052064193&w=1849"),
    ("Lace Trim Shorts",55.90,"black","https://www.zara.com/ca/en/lace-trim-shorts-p02194827.html","https://static.zara.net/assets/public/d94e/d3fd/e50f475faae1/a9c86071a1f6/02194827800-p/02194827800-p.jpg?ts=1774005481182&w=1849"),
    ("Mini Pocket Shorts",45.90,"black","https://www.zara.com/ca/en/mini-pocket-shorts-p03067420.html","https://static.zara.net/assets/public/deae/7f68/57254a04a1cb/8f3c100affd9/03067410044-a2/03067410044-a2.jpg?ts=1771259883401&w=1849"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Shorts","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Jackets/Coats (Round 3)
for name, price, color, cat, style, url, img in [
    ("Faux Leather Jacket",139.00,"black","Jacket","casual","https://www.zara.com/ca/en/faux-leather-jacket-p04391892.html","https://static.zara.net/assets/public/1ab2/2525/e79347469d55/6d8787a6603f/04341892700-a2/04341892700-a2.jpg?ts=1771940730323&w=1809"),
    ("Faux Leather Bomber Jacket",139.00,"beige","Jacket","casual","https://www.zara.com/ca/en/faux-leather-bomber-jacket-p04749752.html","https://static.zara.net/assets/public/761f/8857/49274555bb79/fd035850df85/04749752733-a1/04749752733-a1.jpg?ts=1771937012908&w=1809"),
    ("Hooded Balloon Jacket",79.90,"black","Jacket","sporty","https://www.zara.com/ca/en/hooded-balloon-jacket-p08372095.html","https://static.zara.net/assets/public/7349/779b/d5554c74bc5d/2dd5d8dd7f8a/08372095715-a3/08372095715-a3.jpg?ts=1772636272438&w=1809"),
    ("Belted Linen Safari Jacket",79.90,"brown","Jacket","casual","https://www.zara.com/ca/en/belted-linen-safari-jacket-p02587801.html","https://static.zara.net/assets/public/7b72/b7b5/a0cb4d7c8b7c/a2218faf3911/02587801309-a2/02587801309-a2.jpg?ts=1774886074953&w=1809"),
    ("Crochet Lapel Safari Jacket",89.90,"beige","Jacket","casual","https://www.zara.com/ca/en/crochet-lapel-safari-jacket-p08372063.html","https://static.zara.net/assets/public/8952/7d54/f0cb49a4b197/d6e8b6a59841/08372063075-p/08372063075-p.jpg?ts=1773851106197&w=1809"),
    ("Linen Belted Trench Coat",99.90,"green","Coat","formal","https://www.zara.com/ca/en/linen-blend-belted-trench-jacket-p02753364.html","https://static.zara.net/assets/public/d809/4e91/e5524654b075/d279143a0028/02753364510-a2/02753364510-a2.jpg?ts=1774884878384&w=1809"),
    ("Washed Effect Short Trench Coat",75.90,"brown","Coat","casual","https://www.zara.com/ca/en/washed-effect-short-trench-coat-p02634787.html","https://static.zara.net/assets/public/9aaa/d810/5ff7469fa552/927e553915e8/02634787704-p/02634787704-p.jpg?ts=1774015564797&w=1809"),
    ("High Collar Jacket",89.90,"white","Jacket","formal","https://www.zara.com/ca/en/high-collar-jacket-p06929270.html","https://static.zara.net/assets/public/3464/8799/0d91453191f8/ad00531be264/06929270251-p/06929270251-p.jpg?ts=1772715144658&w=1809"),
    ("Tailored Blazer with Lapel Buttons",109.00,"brown","Jacket","formal","https://www.zara.com/ca/en/tailored-buttoned-lapel-blazer-p02736494.html","https://static.zara.net/assets/public/116b/afa6/e89449058f2e/3cb61358f8c9/02736494707-000-p/02736494707-000-p.jpg?ts=1774885635368&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":cat,"color":color,"style":style,"price":str(price),"image_url":img,"url":url})

# Zara Pants (Round 3)
for name, price, color, url, img in [
    ("Oversize Cargo Pants",65.90,"black","https://www.zara.com/ca/en/oversized-cargo-pants-p01300015.html","https://static.zara.net/assets/public/9425/dc5f/2d9a47d28050/1677e8a4997a/01300015800-p/01300015800-p.jpg?ts=1773250011390&w=1809"),
    ("ZW Linen Barrel Pants Mauve",79.90,"pink","https://www.zara.com/ca/en/zw-collection-linen-barrel-pants-p04344045.html","https://static.zara.net/assets/public/5285/e1ea/025248d08224/d8af274b6227/04344045619-f1/04344045619-f1.jpg?ts=1773995339310&w=1769"),
    ("Elastic Waist Barrel Pants",59.90,"gray","https://www.zara.com/ca/en/barrel-pants-with-elastic-waist-p01478020.html","https://static.zara.net/assets/public/40ed/6a12/e53549ea9a19/6e1119060d0c/01478020922-f1/01478020922-f1.jpg?ts=1770907427178&w=1769"),
    ("Linen Straight Leg Pants",59.90,"beige","https://www.zara.com/ca/en/linen-straight-leg-pants-p09929141.html","https://static.zara.net/assets/public/263c/249e/c84b4e85bc52/393cb728aa33/09929141052-f1/09929141052-f1.jpg?ts=1774942925307&w=1769"),
    ("Barrel Pants Rose",59.90,"pink","https://www.zara.com/ca/en/barrel-pants-with-elastic-waist-p01478020.html","https://static.zara.net/assets/public/8230/6278/29ff4a5a8656/d664d104ce7e/01478020622-f1/01478020622-f1.jpg?ts=1770907423266&w=1769"),
    ("ZW Linen Barrel Pants Brown",79.90,"brown","https://www.zara.com/ca/en/zw-collection-linen-barrel-pants-p04344045.html","https://static.zara.net/assets/public/da85/3796/d60549228f12/c534f956a29d/04344045700-f1/04344045700-f1.jpg?ts=1773995332378&w=1769"),
    ("Drawstring Satin Pants",55.90,"black","https://www.zara.com/ca/en/drawstring-satin-pants-p02180415.html","https://static.zara.net/assets/public/20ff/1d13/72f447bc93e9/3edcf4b9ff6f/03152442800-f1/03152442800-f1.jpg?ts=1774939660437&w=1769"),
    ("ZW Vented Linen Pants",69.90,"black","https://www.zara.com/ca/en/zw-collection-linen-pants-with-vents-p01936334.html","https://static.zara.net/assets/public/cf36/deea/4f2d4ea58389/676ab77fb61a/04344041800-f1/04344041800-f1.jpg?ts=1774948148996&w=1769"),
    ("Wide-Leg Linen Pants",69.90,"brown","https://www.zara.com/ca/en/wide-leg-linen-pants-p02574771.html","https://static.zara.net/assets/public/be9e/0961/26aa4fc1b2f5/0db3c3a2bc90/02574771700-f1/02574771700-f1.jpg?ts=1772624051807&w=1769"),
    ("ZW Striped Barrel Pants",69.90,"white","https://www.zara.com/ca/en/zw-collection-striped-barrel-pants-p01928355.html","https://static.zara.net/assets/public/9f5e/31e9/2f4d4d8fb5a8/bd52155fc7b7/01928355104-f1/01928355104-f1.jpg?ts=1774355023427&w=1769"),
    ("Elastic Waist Pants Curry",65.90,"yellow","https://www.zara.com/ca/en/elastic-waist-pants-p01255413.html","https://static.zara.net/assets/public/8414/ddd7/450e478e89fc/17f5acda6fa8/04661417809-f1/04661417809-f1.jpg?ts=1773826182457&w=1769"),
    ("Flare Linen Pants",79.90,"yellow","https://www.zara.com/ca/en/flowy-linen-blend-pants-with-slits-p02602801.html","https://static.zara.net/assets/public/a208/b4eb/a11840e8add8/45baaccc02c3/04786056802-000-a4/04786056802-000-a4.jpg?ts=1774956671123&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Pants","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara T-shirts (Round 3)
for name, price, color, url, img in [
    ("Rib Sleeveless Top",22.90,"white","https://www.zara.com/ca/en/rib-sleeveless-top-p02335180.html","https://static.zara.net/assets/public/00d8/8ada/b71a45ce9a66/163d3e228f73/02335180711-a1/02335180711-a1.jpg?ts=1775490574875&w=1809"),
    ("Ribbed Sleeveless Top",15.90,"white","https://www.zara.com/ca/en/ribbed-sleeveless-top-p03253301.html","https://static.zara.net/assets/public/c01e/4980/05ae42b7a253/4e26c88cf3d8/05862051406-a2/05862051406-a2.jpg?ts=1770033673032&w=1809"),
    ("Fluid Shoulder Pad T-Shirt",35.90,"black","https://www.zara.com/ca/en/fluid-sleeveless-shoulder-pad-top-p05644029.html","https://static.zara.net/assets/public/c8dc/33da/0360471d8c6b/5142b9cc3b2e/05644043800-000-a1/05644043800-000-a1.jpg?ts=1775660533174&w=1809"),
    ("Cotton V-Neck T-Shirt",19.90,"white","https://www.zara.com/ca/en/cotton-v-neck-t-shirt-p04174301.html","https://static.zara.net/assets/public/e0f5/e0de/4e5341d3ab1e/9bdb5d2b4b77/04174301250-a1/04174301250-a1.jpg?ts=1770981852895&w=1809"),
    ("Raised Flower T-Shirt",32.90,"white","https://www.zara.com/ca/en/raised-floral-t-shirt-p04805032.html","https://static.zara.net/assets/public/4ab3/ae06/a39947ca9006/fe95c3abc0d2/04805032250-a1/04805032250-a1.jpg?ts=1775664932752&w=1809"),
    ("Off-The-Shoulder T-Shirt",22.90,"black","https://www.zara.com/ca/en/off-the-shoulder-t-shirt-p02335179.html","https://static.zara.net/assets/public/fa9e/ec98/dcd946c18168/c46d4ec6350b/02335179800-a2/02335179800-a2.jpg?ts=1775062927622&w=1809"),
    ("Embroidered Rib T-Shirt",32.90,"white","https://www.zara.com/ca/en/embroidered-rib-short-sleeve-t-shirt-p05643036.html","https://static.zara.net/assets/public/6fbd/4c77/0bfc462ca7fa/1cb5bcfb4361/05643036250-p/05643036250-p.jpg?ts=1775638268067&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"T-shirt","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Skirts (Round 3)
for name, price, color, url, img in [
    ("Polka Dot Satin Midi Skirt",45.90,"black","https://www.zara.com/ca/en/satin-effect-midi-skirt-p08338537.html","https://static.zara.net/assets/public/2b43/8448/eae84c5f82f6/913f6091da05/08338404070-p/08338404070-p.jpg?ts=1774970886875&w=1809"),
    ("Animal Print Tulle Skirt",39.90,"brown","https://www.zara.com/ca/en/animal-print-tulle-skirt-p05039408.html","https://static.zara.net/assets/public/2b93/5fda/0b084bec92df/a39a46cf821a/05039408042-p/05039408042-p.jpg?ts=1775476118147&w=1809"),
    ("Wrinkled Knit Midi Skirt",65.90,"gray","https://www.zara.com/ca/en/wrinkled-effect-knit-midi-skirt-p02893016.html","https://static.zara.net/assets/public/97c5/cc7c/46bd47339453/b7d54295bdef/02893016081-p/02893016081-p.jpg?ts=1774619602982&w=1809"),
    ("Ramie Plaid Midi Skirt",99.90,"blue","https://www.zara.com/ca/en/ramie-plaid-midi-skirt-zw-collection-p04043036.html","https://static.zara.net/assets/public/0557/9fa4/cdfe47cf84b2/625c02d77cd9/04043036406-a1/04043036406-a1.jpg?ts=1774857520493&w=1809"),
    ("Asymmetric Skort",55.90,"black","https://www.zara.com/ca/en/asymmetric-skort-with-applique-p01971241.html","https://static.zara.net/assets/public/efcb/7bf2/395d4c7db94e/dfbba43e4d52/01971241800-a1/01971241800-a1.jpg?ts=1775046636397&w=1809"),
    ("Sequin Mini Skirt",55.90,"brown","https://www.zara.com/ca/en/sequin-mini-skirt-p02157058.html","https://static.zara.net/assets/public/64bb/e2e0/47cd4562a50e/2e53757e1622/02157058870-a2/02157058870-a2.jpg?ts=1775062922128&w=1809"),
    ("Satin Midi Skirt",55.90,"brown","https://www.zara.com/ca/en/satin-midi-skirt-p08160399.html","https://static.zara.net/assets/public/a372/7685/57f4428eaafa/2ab539e095d4/08160399700-p/08160399700-p.jpg?ts=1765876073632&w=1809"),
    ("Faux Leather Belted Midi Skirt",65.90,"brown","https://www.zara.com/ca/en/faux-leather-belted-midi-skirt-p04387245.html","https://static.zara.net/assets/public/9bed/a58b/0a3d417ca2dc/aecf6138c191/04387245681-a4/04387245681-a4.jpg?ts=1766505936532&w=1809"),
    ("Wrap Midi Skirt",55.90,"green","https://www.zara.com/ca/en/wrap-midi-skirt-p04391446.html","https://static.zara.net/assets/public/a101/2101/5f8147e3a34c/b0ec3eb6446d/04391446644-p/04391446644-p.jpg?ts=1774371058466&w=1809"),
    ("Layered Midi Skirt",45.90,"white","https://www.zara.com/ca/en/layered-midi-skirt-p04387079.html","https://static.zara.net/assets/public/f066/1f4b/0d064a33a5a9/ae53e5e9d6bf/04387060250-a3/04387060250-a3.jpg?ts=1772806183354&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Skirt","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Jeans (Round 3)
for name, price, color, url, img in [
    ("TRF Mid-Rise Belted Jeans",69.90,"blue","https://www.zara.com/ca/en/trf-mid-rise-belted-jeans-p08727029.html","https://static.zara.net/assets/public/0ca2/ea08/25f94f1c9488/4dce87a8ae10/402100ecea16cb963fc2384477a09484/402100ecea16cb963fc2384477a09484.jpg?ts=1775687173552&w=1824"),
    ("TRF High Waist Wide Leg Jeans",65.90,"blue","https://www.zara.com/ca/en/trf-high-waist-wide-leg-jeans-p05575229.html","https://static.zara.net/assets/public/54a5/62b1/06244f9ba703/c53d202aac11/f4f2062fc8b860126dc3fe05039684aa/f4f2062fc8b860126dc3fe05039684aa.jpg?ts=1775045503495&w=1824"),
    ("ZW Ankle Relaxed Jeans",65.90,"blue","https://www.zara.com/ca/en/zw-collection-ankle-relaxed-mid-rise-jeans-p08307045.html","https://static.zara.net/assets/public/9162/4ec9/9f4640e4a606/1fbfd5fdd9ce/0a3c1dde02d7d57739b439db5c7dc7f1/0a3c1dde02d7d57739b439db5c7dc7f1.jpg?ts=1774868605719&w=1824"),
    ("TRF Mid-Rise Fold-Up Straight Jeans",55.90,"blue","https://www.zara.com/ca/en/trf-mid-rise-fold-up-straight-leg-jeans-p04730139.html","https://static.zara.net/assets/public/31f5/b42b/a4a541d2b2af/563fe5f54c8f/image-2dsk-993cbac3-a814-4b02-9adc-75b26c1a2214-default/image-2dsk-993cbac3-a814-4b02-9adc-75b26c1a2214-default.jpg?ts=1774887291699&w=1824"),
    ("TRF Folded Waist Mid-Rise Jeans",69.90,"blue","https://www.zara.com/ca/en/trf-folded-waist-mid-rise-jeans-p05252014.html","https://static.zara.net/assets/public/6989/f003/751743629be4/3e516eda946b/56bdd11be111d399ad16e9a76824cf49/56bdd11be111d399ad16e9a76824cf49.jpg?ts=1774643394021&w=1824"),
    ("Z1975 Wide Leg Dart Jeans",65.90,"blue","https://www.zara.com/ca/en/z1975-mid-rise-wide-leg-jeans-with-darts-p01416026.html","https://static.zara.net/assets/public/b7f5/619d/c09d4c05bea3/8083c2df4db4/01416026724-f1/01416026724-f1.jpg?ts=1772005360692&w=1824"),
    ("Z1975 High-Waist Mom Fit Jeans",55.90,"blue","https://www.zara.com/ca/en/z-05-high-waist-mom-fit-jeans-p04083022.html","https://static.zara.net/assets/public/b1a8/9b53/af2d4c6786ff/a27414e403d9/7588fddd0098c603b319f0661c13038e/7588fddd0098c603b319f0661c13038e.jpg?ts=1775042074961&w=1824"),
    ("Z1975 High Waist Straight Jeans",59.90,"blue","https://www.zara.com/ca/en/z1975-high-waist-straight-long-length-jeans-p08228021.html","https://static.zara.net/assets/public/8b8a/a487/556b4146b3c8/9ca1b15de9a6/f033f99594f67fc6aee725d1e8847007/f033f99594f67fc6aee725d1e8847007.jpg?ts=1775041277475&w=1824"),
    ("TRF Mid-Rise Baggy Balloon Jeans",65.90,"blue","https://www.zara.com/ca/en/trf-mid-rise-baggy-balloon-jeans-p05762040.html","https://static.zara.net/assets/public/0a02/30d0/45ce41429d8c/8a4aaf8a3ef3/image-2dsk-4e807059-97ad-4064-a308-c960ffb6acfd-default/image-2dsk-4e807059-97ad-4064-a308-c960ffb6acfd-default.jpg?ts=1774951296790&w=1824"),
    ("ZW High-Waist Wide Leg Jeans",65.90,"blue","https://www.zara.com/ca/en/zw-collection-high-waist-wide-leg-jeans-p08246053.html","https://static.zara.net/assets/public/882f/ccfc/1425485289b9/e88a4744725b/08307251407-f1/08307251407-f1.jpg?ts=1769216578711&w=1824"),
    ("TRF Low Rise Wide Leg Jeans",65.90,"blue","https://www.zara.com/ca/en/trf-low-rise-wide-leg-jeans-p08727022.html","https://static.zara.net/assets/public/a937/b8d1/397a4e0388b0/c8b7ed86c5e8/06929022422-f1/06929022422-f1.jpg?ts=1769013665708&w=1824"),
    ("TRF High-Waist Wide Leg Jeans Dark",65.90,"black","https://www.zara.com/ca/en/trf-high-waist-wide-leg-jeans-p06688226.html","https://static.zara.net/assets/public/b2c3/a1f1/024147818586/40d30d42dc66/06688226400-f1/06688226400-f1.jpg?ts=1770039467396&w=1824"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Jeans","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Knitwear/Sweaters (Round 3)
for name, price, color, url, img in [
    ("Puff Sleeve Cardigan",65.90,"navy","https://www.zara.com/ca/en/cardigan-with-puff-sleeves-and-slits-p04192080.html","https://static.zara.net/assets/public/33e1/c591/4c0a416993fb/9f0055c52eef/04192080401-p/04192080401-p.jpg?ts=1775552282286&w=1809"),
    ("Fine Knit V-Neck Jumper",55.90,"black","https://www.zara.com/ca/en/fine-knit-v-neck-jumper-p08779006.html","https://static.zara.net/assets/public/0230/6a81/d1c4453db789/716d116ab2b6/08779006800-a1/08779006800-a1.jpg?ts=1775645478201&w=1809"),
    ("Floral Textured Knit Halter Top",79.90,"beige","https://www.zara.com/ca/en/floral-textured-knit-halter-top-p03920171.html","https://static.zara.net/assets/public/437e/58d7/192c489c9e4f/22846a6ea3d0/03920171710-a3/03920171710-a3.jpg?ts=1775552276548&w=1809"),
    ("Fringed Knit Top",55.90,"beige","https://www.zara.com/ca/en/fringed-knit-top-p03920295.html","https://static.zara.net/assets/public/9b94/07f1/430846ebb3b7/8f3bb25091b2/03920295712-a1/03920295712-a1.jpg?ts=1775552277868&w=1809"),
    ("Short Sleeve Knit Jacket",55.90,"beige","https://www.zara.com/ca/en/short-sleeve-knit-cardigan-with-lace-trim-p03920182.html","https://static.zara.net/assets/public/c085/aa63/27b548b9b91b/8a9243182930/03920182834-a1/03920182834-a1.jpg?ts=1770811029749&w=1809"),
    ("Cropped Knit Jumper",79.90,"beige","https://www.zara.com/ca/en/cropped-knit-jumper-with-intertwined-tape-p00021012.html","https://static.zara.net/assets/public/e89d/597c/99ce457fba63/ee316e11d008/00021012712-a1/00021012712-a1.jpg?ts=1775638360881&w=1809"),
    ("Knit Jacket with Bows",79.90,"pink","https://www.zara.com/ca/en/knit-jacket-with-bows-p09598022.html","https://static.zara.net/assets/public/8801/d7d5/6d5e48c4ae75/c87db3e1d3d8/09598022046-a1/09598022046-a1.jpg?ts=1774267250805&w=1809"),
    ("Flowy V-Neck Jumper",45.90,"white","https://www.zara.com/ca/en/flowy-v-neck-jumper-p03471006.html","https://static.zara.net/assets/public/0b27/a547/a0b74033b7e0/6592b3a01b5c/00858038250-1-a1/00858038250-1-a1.jpg?ts=1772191932353&w=1809"),
    ("Beaded Neck Knit Top",59.90,"blue","https://www.zara.com/ca/en/knit-beaded-neck-top-p03921034.html","https://static.zara.net/assets/public/5f20/14d6/7187409b9be1/a2b2730e6a57/03921034400-p/03921034400-p.jpg?ts=1775662018322&w=1809"),
    ("Knit Corset Top",55.90,"black","https://www.zara.com/ca/en/knit-corset-top-p02142122.html","https://static.zara.net/assets/public/1f5c/55d3/5923d18477b7/0d1c2d56f508/02142142212-a1/02142142212-a1.jpg?ts=1775657510010&w=1809"),
    ("V-Neck Knit Jumper",69.90,"beige","https://www.zara.com/ca/en/v-neck-knit-jumper-p02142216.html","https://static.zara.net/assets/public/fb40/deeb/23f90a10b7dc/148742da7fba/02142221612-a1/02142221612-a1.jpg?ts=1775657510077&w=1809"),
    ("Ribbed Knit Halter Top",35.90,"black","https://www.zara.com/ca/en/ribbed-knit-halter-top-p03519002.html","https://static.zara.net/assets/public/fc79/6257/65dc420a9698/1a71c6f28da3/06236025303-p/06236025303-p.jpg?ts=1775657512409&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Sweater","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# Zara Dresses (Round 3)
for name, price, color, url, img in [
    ("ZW Linen Midi Dress",99.90,"beige","https://www.zara.com/ca/en/zw-collection-linen-midi-dress-p04786048.html","https://static.zara.net/assets/public/0886/a18c/f4fb462381b6/33b312685bb6/04786048802-p/04786048802-p.jpg?ts=1774949052568&w=1809"),
    ("ZW Linen Blend Midi Dress",129.00,"gray","https://www.zara.com/ca/en/zw-collection-linen-blend-midi-dress-p02103901.html","https://static.zara.net/assets/public/7cd7/ffb7/734445c68d85/25d204e1da27/02103901081-a1/02103901081-a1.jpg?ts=1774949037102&w=1809"),
    ("Gingham Check Shirt Dress",99.90,"green","https://www.zara.com/ca/en/gingham-check-shirt-dress-zw-collection-p02507041.html","https://static.zara.net/assets/public/26eb/15e6/2da4455eb848/e97889bbbeba/02507041500-h1/02507041500-h1.jpg?ts=1770386339684&w=1809"),
    ("Flowy Long Dress",65.90,"black","https://www.zara.com/ca/en/flowy-long-dress-p05644026.html","https://static.zara.net/assets/public/8899/2630/85e94a6fa4a9/07efcca07f13/05644026800-1-p/05644026800-1-p.jpg?ts=1773665737998&w=1809"),
    ("Belted Linen Midi Dress",79.90,"blue","https://www.zara.com/ca/en/belted-linen-blend-midi-dress-p04745035.html","https://static.zara.net/assets/public/29a7/7148/4faf47498a48/28eb2a67cdc3/04745035400-p/04745035400-p.jpg?ts=1773412578951&w=1809"),
    ("Combination Midi Dress",79.90,"gray","https://www.zara.com/ca/en/combination-midi-dress-p03897187.html","https://static.zara.net/assets/public/30e1/2c62/4e6c43b0a193/d5127b36f157/03897187809-p/03897187809-p.jpg?ts=1768567583312&w=1809"),
    ("Gingham Midi Dress",69.90,"blue","https://www.zara.com/ca/en/gingham-check-midi-dress-p03152308.html","https://static.zara.net/assets/public/f9e8/8afa/5cf9487786dc/a978854e6f67/03152308044-p/03152308044-p.jpg?ts=1769788009831&w=1809"),
    ("Trench Midi Dress",69.90,"beige","https://www.zara.com/ca/en/trench-midi-dress-p03067310.html","https://static.zara.net/assets/public/76f9/ef12/db87494492f3/f3222d3017b3/03067310726-p/03067310726-p.jpg?ts=1769789946887&w=1809"),
    ("Short Knotted Shirtdress",79.90,"blue","https://www.zara.com/ca/en/short-knotted-shirtdress-p02689859.html","https://static.zara.net/assets/public/7de7/15f8/8d9743b291b4/d55b587c5f11/02689859044-a1/02689859044-a1.jpg?ts=1774455299468&w=1809"),
    ("Striped Lace Mini Dress",69.90,"pink","https://www.zara.com/ca/en/striped-lace-mini-dress-p02581532.html","https://static.zara.net/assets/public/d054/59a9/0dae44418900/985120ddff2c/02581532620-a1/02581532620-a1.jpg?ts=1774344737582&w=1809"),
    ("ZW Asymmetric Midi Dress",99.90,"red","https://www.zara.com/ca/en/zw-collection-asymmetric-midi-dress-p02102098.html","https://static.zara.net/assets/public/d818/2684/c99b4589a1a7/17d73afcb7fc/02102099632-a2/02102099632-a2.jpg?ts=1774611533942&w=1809"),
    ("ZW Printed Dress with Ties",149.00,"yellow","https://www.zara.com/ca/en/zw-collection-printed-dress-with-ties-p02109098.html","https://static.zara.net/assets/public/4ac4/1ecc/4aed413a9acd/cd48341b0b71/02109098300-p/02109098300-p.jpg?ts=1774611541228&w=1809"),
    ("Striped Belted Midi Dress",79.90,"yellow","https://www.zara.com/ca/en/striped-belted-midi-dress-p03293054.html","https://static.zara.net/assets/public/3ce7/f9bf/3e6340d7bbad/dab71e0bbba4/03293054047-p/03293054047-p.jpg?ts=1774009907867&w=1809"),
    ("Striped Mini Dress",65.90,"red","https://www.zara.com/ca/en/striped-mini-dress-p03293055.html","https://static.zara.net/assets/public/8365/2cd1/4bb04f2487c4/e8ea6224bdec/03293055061-a1/03293055061-a1.jpg?ts=1774009907751&w=1809"),
    ("Belted Midi Dress Brown",79.90,"brown","https://www.zara.com/ca/en/belted-midi-dress-p02343572.html","https://static.zara.net/assets/public/78f7/a845/4f31467a81ce/1af94df76f5e/02343572700-p/02343572700-p.jpg?ts=1769615292799&w=1809"),
    ("Cut Out Lace Dress",65.90,"black","https://www.zara.com/ca/en/lace-cut-out-dress-p01067002.html","https://static.zara.net/assets/public/db56/2759/c7134210b104/7f752d9e4390/05030019800-p/05030019800-p.jpg?ts=1774614243295&w=1809"),
    ("Combination Lace Dress",65.90,"black","https://www.zara.com/ca/en/combination-lace-dress-p01067004.html","https://static.zara.net/assets/public/e74e/45b1/f6bf4a4796a2/686ab6a25d53/05039020800-p/05039020800-p.jpg?ts=1774614282344&w=1809"),
    ("Belted Striped Halter Dress",45.90,"brown","https://www.zara.com/ca/en/striped-halter-dress-with-belt-p05063353.html","https://static.zara.net/assets/public/4c86/9bf6/8aa34b8cbdcb/a0169de02cc9/05063353178-h/05063353178-h.jpg?ts=1775052058429&w=1809"),
    ("Halter Swing Dress Yellow",65.90,"yellow","https://www.zara.com/ca/en/swing-halter-dress-p02739111.html","https://static.zara.net/assets/public/a47b/f0d9/b6da416f9e7e/6121957c1693/02739111300-a1/02739111300-a1.jpg?ts=1775064957420&w=1809"),
    ("Swing Halter Dress White",65.90,"white","https://www.zara.com/ca/en/halter-swing-dress-p03152380.html","https://static.zara.net/assets/public/e701/7e09/f6fd4ed79daf/f2d45bb69357/03152380251-p/03152380251-p.jpg?ts=1775052502188&w=1809"),
    ("Long Tulle Dress",65.90,"brown","https://www.zara.com/ca/en/long-combination-tulle-dress-p05584354.html","https://static.zara.net/assets/public/beb9/d8c5/d7fc41d7b992/4dc2584fb617/05584354716-a2/05584354716-a2.jpg?ts=1771432734088&w=1809"),
    ("Ruffled Mini Dress",65.90,"white","https://www.zara.com/ca/en/ruffled-mini-dress-p07521329.html","https://static.zara.net/assets/public/c971/600e/ac3341828cb3/b5a0e1ef42b5/07521329250-p/07521329250-p.jpg?ts=1775052086854&w=1809"),
    ("Short Textured Dress",55.90,"beige","https://www.zara.com/ca/en/short-textured-dress-p05067276.html","https://static.zara.net/assets/public/2707/0a4b/790849ccb279/03c5f4b0fd2f/05067276712-a1/05067276712-a1.jpg?ts=1775032929204&w=1809"),
    ("Floral Print Bow Belt Dress",89.90,"pink","https://www.zara.com/ca/en/floral-print-bow-belt-dress-p02298057.html","https://static.zara.net/assets/public/a03e/6093/454841889f9b/6d33b4d29155/02298057330-p/02298057330-p.jpg?ts=1772198709624&w=1809"),
    ("Floral Satin Midi Dress",69.90,"white","https://www.zara.com/ca/en/floral-satin-effect-midi-dress-p02742306.html","https://static.zara.net/assets/public/069f/f50d/9e6147ac9b60/fc24549f836c/02742306252-p/02742306252-p.jpg?ts=1774970840746&w=1809"),
    ("Puff Sleeve Short Dress",79.90,"white","https://www.zara.com/ca/en/short-balloon-sleeve-dress-p03897114.html","https://static.zara.net/assets/public/7a10/8d70/fdf54144be38/15188c083573/03897114064-h1/03897114064-h1.jpg?ts=1775046640074&w=1809"),
    ("Flowy Halter Dress",65.90,"blue","https://www.zara.com/ca/en/flowy-halter-dress-p06929089.html","https://static.zara.net/assets/public/194a/32c1/4b304b2ca1b2/cde824ac5ba2/06929089406-p/06929089406-p.jpg?ts=1774971514595&w=1809"),
    ("Satin Mini Dress with Sash",55.90,"white","https://www.zara.com/ca/en/satin-effect-sash-mini-dress-p02745533.html","https://static.zara.net/assets/public/7ef5/932e/1bd240979241/f5bce214737d/02745533300-a1/02745533300-a1.jpg?ts=1774971516883&w=1809"),
]:
    products.append({"name":name,"brand":"ZARA","cat":"Dress","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# H&M Tops (Round 3)
for name, price, color, cat, url, img in [
    ("Linen-Blend Lace-Detail Top",24.99,"white","T-shirt","https://www2.hm.com/en_ca/productpage.1341362001.html","https://image.hm.com/assets/hm/c1/7d/c17d6b3193bb8d9a957104136b93be6ba19ec698.jpg?imwidth=1536"),
    ("Short Rugby Shirt",24.99,"yellow","Shirt","https://www2.hm.com/en_ca/productpage.1342507001.html","https://image.hm.com/assets/hm/43/5d/435dac685a605c7abbc23614ede6b993f8ff069f.jpg?imwidth=1536"),
    ("Strappy Top with Eyelet Embroidery",24.99,"white","T-shirt","https://www2.hm.com/en_ca/productpage.1335330001.html","https://image.hm.com/assets/hm/02/b6/02b68ddc6b995d2ab6391adbacbfb6b6c0355860.jpg?imwidth=1536"),
    ("Rib-Knit Polo Shirt",24.99,"yellow","Shirt","https://www2.hm.com/en_ca/productpage.1340104001.html","https://image.hm.com/assets/hm/93/dd/93dda515999e1349fd6f4ec81038deb206925123.jpg?imwidth=1536"),
]:
    products.append({"name":name,"brand":"H&M","cat":cat,"color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# H&M Jeans (Round 3)
for name, price, color, url, img in [
    ("Wide-Leg Jeans",24.99,"blue","https://www2.hm.com/en_ca/productpage.1341364001.html","https://image.hm.com/assets/hm/ba/99/ba99041cc4fde0072d78d33093cba12172964129.jpg?imwidth=1536"),
    ("Barrel Leg Regular Waist Jeans",24.99,"beige","https://www2.hm.com/en_ca/productpage.1329166001.html","https://image.hm.com/assets/hm/af/23/af23850bca54f18833d7cfb5578e66e1238591d1.jpg?imwidth=1536"),
]:
    products.append({"name":name,"brand":"H&M","cat":"Jeans","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# H&M Dresses & Boots (Round 3)
for name, price, color, cat, style, url, img in [
    ("Pintuck Dress with Lace Panel",24.99,"beige","Dress","casual","https://www2.hm.com/en_ca/productpage.1340684001.html","https://image.hm.com/assets/hm/b5/c6/b5c632bf9a8afe3054c59fcd4b41f96a09d97432.jpg?imwidth=1536"),
    ("Knee-High Boots Brown",84.99,"brown","Boots","casual","https://www2.hm.com/en_ca/productpage.1291799002.html","https://image.hm.com/assets/hm/92/26/922674796767528f877c90b434de0e4b3d11be6f.jpg?imwidth=1536"),
    ("Cowboy Boots",84.99,"brown","Boots","casual","https://www2.hm.com/en_ca/productpage.1320067001.html","https://image.hm.com/assets/hm/ac/d8/acd8da325293a335cf522304629094e2d9011d54.jpg?imwidth=1536"),
    ("Pointed-Toe Ankle Boots",59.99,"beige","Boots","formal","https://www2.hm.com/en_ca/productpage.1312618002.html","https://image.hm.com/assets/hm/eb/90/eb905a681ff2433f693593a57798a298d340da37.jpg?imwidth=1536"),
]:
    products.append({"name":name,"brand":"H&M","cat":cat,"color":color,"style":style,"price":str(price),"image_url":img,"url":url})

# H&M Flats (Round 3)
for name, price, color, url, img in [
    ("Deck Shoes Beige",109.00,"beige","https://www2.hm.com/en_ca/productpage.1264544006.html","https://image.hm.com/assets/hm/ae/a1/aea129759bdff12997a1799677d2f7777c90946b.jpg?imwidth=1536"),
    ("Deck Shoes Brown",44.99,"brown","https://www2.hm.com/en_ca/productpage.1313100001.html","https://image.hm.com/assets/hm/40/9a/409a652bdcf5142a577c8e36d3358f44bd29b6d7.jpg?imwidth=1536"),
    ("Leopard Deck Shoes",44.99,"brown","https://www2.hm.com/en_ca/productpage.1313100005.html","https://image.hm.com/assets/hm/31/4f/314fe3b660b87ce8d0fa7d8ea81b936d51dcf42f.jpg?imwidth=1536"),
    ("Leather Deck Shoes",99.00,"brown","https://www2.hm.com/en_ca/productpage.1319372001.html","https://image.hm.com/assets/hm/b2/45/b24566ebc482b7b0e13c24de0994cbdda8a25c3f.jpg?imwidth=1536"),
]:
    products.append({"name":name,"brand":"H&M","cat":"Flats","color":color,"style":"casual","price":str(price),"image_url":img,"url":url})

# H&M Heels (Round 3)
for name, price, color, url, img in [
    ("Heeled Espadrilles",74.99,"beige","https://www2.hm.com/en_ca/productpage.1324440001.html","https://image.hm.com/assets/hm/79/b4/79b42e8ecd984af6f3884437a19bb5992ffd2a62.jpg?imwidth=1536"),
    ("Kitten-Heeled Sandals Beige",34.99,"beige","https://www2.hm.com/en_ca/productpage.1321306002.html","https://image.hm.com/assets/hm/29/ee/29eeda8b5b053394287aa646694796bc6d4a06d6.jpg?imwidth=1536"),
    ("Block-Heeled Pumps Beige",49.99,"beige","https://www2.hm.com/en_ca/productpage.1321315002.html","https://image.hm.com/assets/hm/70/50/705015f4a4d3f8f3e7f1d6eff521cfafd91f186a.jpg?imwidth=1536"),
    ("Wedge-Heeled Sandals Black",59.99,"black","https://www2.hm.com/en_ca/productpage.1331703001.html","https://image.hm.com/assets/hm/b0/9b/b09b2cbdd24ec3a5d420360cd1b2e245347745ae.jpg?imwidth=1536"),
    ("Pointed Suede Slingbacks Green",74.99,"green","https://www2.hm.com/en_ca/productpage.1312645002.html","https://image.hm.com/assets/hm/e2/4e/e24efa287126c7fef2ad31a9cbef390921ecf36d.jpg?imwidth=1536"),
    ("Slingback Court Shoes",44.99,"beige","https://www2.hm.com/en_ca/productpage.1338744001.html","https://image.hm.com/assets/hm/70/6c/706c08290d0c4c69353ecf33d40a54325280ac07.jpg?imwidth=1536"),
    ("Slingback Pumps Black",34.99,"black","https://www2.hm.com/en_ca/productpage.1301685014.html","https://image.hm.com/assets/hm/ae/0a/ae0a91afdd0b61cee6ceffd963233cf94278e5e4.jpg?imwidth=1536"),
    ("Wedge-Heeled Sandals Platform",74.99,"black","https://www2.hm.com/en_ca/productpage.1328912001.html","https://image.hm.com/assets/hm/bd/d6/bdd6fb87e60a095c3f9dd739c5913eafbe12f284.jpg?imwidth=1536"),
    ("Pointed Suede Slingbacks Beige",74.99,"beige","https://www2.hm.com/en_ca/productpage.1312645004.html","https://image.hm.com/assets/hm/b1/ad/b1ad842c960546f09c9b357d677566995e298b16.jpg?imwidth=1536"),
    ("Wedge-Heeled Sandals Brown",64.99,"brown","https://www2.hm.com/en_ca/productpage.1321286002.html","https://image.hm.com/assets/hm/ae/82/ae8222bcce65ed7ca7f21e6448755eb449d46b83.jpg?imwidth=1536"),
    ("Kitten-Heeled Slingbacks Brown",34.99,"brown","https://www2.hm.com/en_ca/productpage.1321306001.html","https://image.hm.com/assets/hm/05/4d/054dab22e6518e96f4871e5a4bb33d408f7faccf.jpg?imwidth=1536"),
    ("Kitten-Heeled Pointed Slingbacks",39.99,"beige","https://www2.hm.com/en_ca/productpage.1291726002.html","https://image.hm.com/assets/hm/52/6d/526d09329b05ea4448b0db8cfb997551afed63e8.jpg?imwidth=1536"),
    ("Heeled Platform Clogs",84.99,"brown","https://www2.hm.com/en_ca/productpage.1328020001.html","https://image.hm.com/assets/hm/7b/61/7b6156cb33cbe66cb07577559401b5c7cc3068fb.jpg?imwidth=1536"),
    ("Block-Heeled Platform Sandals",59.99,"beige","https://www2.hm.com/en_ca/productpage.1332803001.html","https://image.hm.com/assets/hm/cc/0b/cc0b7f9bd5ab211c336f8308665d957b91661ebf.jpg?imwidth=1536"),
    ("Heeled Espadrilles Brown",64.99,"brown","https://www2.hm.com/en_ca/productpage.1320438001.html","https://image.hm.com/assets/hm/c6/9d/c69daeb1d58e9530def10ff43c1193b451929abb.jpg?imwidth=1536"),
    ("Kitten-Heeled Slingbacks Beige",39.99,"beige","https://www2.hm.com/en_ca/productpage.1321484002.html","https://image.hm.com/assets/hm/30/81/308127a595bd859bf8ae422355420066adbb60db.jpg?imwidth=1536"),
    ("Kitten-Heeled Leather Slingbacks",109.00,"brown","https://www2.hm.com/en_ca/productpage.1328018001.html","https://image.hm.com/assets/hm/df/9a/df9ac761966c77d12990e1266c2bd17d525230f6.jpg?imwidth=1536"),
    ("Kitten-Heeled Slingbacks Taupe",34.99,"brown","https://www2.hm.com/en_ca/productpage.1312648001.html","https://image.hm.com/assets/hm/7f/99/7f9983ca29de3a05b138c5cc3fd5b7530b933a60.jpg?imwidth=1536"),
    ("Heeled Suede Sandals Green",84.99,"green","https://www2.hm.com/en_ca/productpage.1320361001.html","https://image.hm.com/assets/hm/56/49/56495876f188a2fd373044335d96ca023de4e9e9.jpg?imwidth=1536"),
    ("Bow-Detail Satin Pumps Red",49.99,"red","https://www2.hm.com/en_ca/productpage.1310105002.html","https://image.hm.com/assets/hm/97/a0/97a097046da32b671ed08ab2f4078c0f26e9af16.jpg?imwidth=1536"),
    ("Block-Heeled Pumps Red",49.99,"red","https://www2.hm.com/en_ca/productpage.1321315003.html","https://image.hm.com/assets/hm/fc/1a/fc1aa602a8ce3f210275b4d7f78343336868f9f6.jpg?imwidth=1536"),
    ("Heeled Leather Sandals Red",84.99,"red","https://www2.hm.com/en_ca/productpage.1321459002.html","https://image.hm.com/assets/hm/56/a6/56a6fa203abd9d59602489f848cad8a85fce2d67.jpg?imwidth=1536"),
    ("Pointed Suede Slingbacks Brown",74.99,"brown","https://www2.hm.com/en_ca/productpage.1312645001.html","https://image.hm.com/assets/hm/d0/35/d0354779372ab33e572f72909d97c5a746065cb2.jpg?imwidth=1536"),
    ("Heeled Slingbacks Brown",59.99,"brown","https://www2.hm.com/en_ca/productpage.1321467002.html","https://image.hm.com/assets/hm/5b/81/5b817706dbcc4d776e2644106b712c6a6d5e87af.jpg?imwidth=1536"),
    ("Pointed Satin Pumps Brown",49.99,"brown","https://www2.hm.com/en_ca/productpage.1304321003.html","https://image.hm.com/assets/hm/c1/df/c1dfbc318f4967c6c8d2f1e51696df295a244f7e.jpg?imwidth=1536"),
    ("Bow-Detail Velour Pumps Brown",44.99,"brown","https://www2.hm.com/en_ca/productpage.1304320003.html","https://image.hm.com/assets/hm/d5/38/d5380bd1355fe5bb1a7e5027720dcdf19c00b8df.jpg?imwidth=1536"),
    ("Block-Heeled Sandals Black",64.99,"black","https://www2.hm.com/en_ca/productpage.1337021001.html","https://image.hm.com/assets/hm/17/90/1790c14341e10b670bae498bce803550ba062acc.jpg?imwidth=1536"),
    ("Pointed Suede Slingbacks Khaki",74.99,"green","https://www2.hm.com/en_ca/productpage.1312645003.html","https://image.hm.com/assets/hm/42/d5/42d5c1ff32626aa26cc8452a37054b1c0d447a0a.jpg?imwidth=1536"),
    ("Heeled Sandals Cream",59.99,"beige","https://www2.hm.com/en_ca/productpage.1320360001.html","https://image.hm.com/assets/hm/3b/fe/3bfe11d3151d1a574610a238104a2f0edca7f7f2.jpg?imwidth=1536"),
    ("Heeled Sandals Brown",59.99,"brown","https://www2.hm.com/en_ca/productpage.1320360002.html","https://image.hm.com/assets/hm/ac/ae/acae108dc4ccc06e7e8f910337318be0d8455b32.jpg?imwidth=1536"),
    ("Kitten-Heeled Slingbacks Green",44.99,"green","https://www2.hm.com/en_ca/productpage.1321486001.html","https://image.hm.com/assets/hm/6e/68/6e68d9d93529e81b09453c8b7c479d419373d68d.jpg?imwidth=1536"),
    ("Kitten-Heeled Leather Slingbacks Beige",84.99,"beige","https://www2.hm.com/en_ca/productpage.1321447002.html","https://image.hm.com/assets/hm/42/db/42dbc73eff1c9dbbbf9b0f45407f42a16a6e8961.jpg?imwidth=1536"),
    ("Heeled Strappy Sandals Green",44.99,"green","https://www2.hm.com/en_ca/productpage.1321299002.html","https://image.hm.com/assets/hm/e9/60/e960f14a28ac17270ea7b9c711592eda2d5edde7.jpg?imwidth=1536"),
    ("Pointed Satin Pumps Black",49.99,"black","https://www2.hm.com/en_ca/productpage.1304321001.html","https://image.hm.com/assets/hm/48/6e/486e00ef9b41229a5b1700d01dff074ca148b0c1.jpg?imwidth=1536"),
    ("Heeled Suede Sandals Brown",84.99,"brown","https://www2.hm.com/en_ca/productpage.1320361002.html","https://image.hm.com/assets/hm/9a/61/9a61bcd16f74206e6ac0981ad513815ae24c9e1e.jpg?imwidth=1536"),
]:
    products.append({"name":name,"brand":"H&M","cat":"Heels","color":color,"style":"formal","price":str(price),"image_url":img,"url":url})

# H&M Shorts & Jacket (Round 3)
for name, price, color, cat, style, url, img in [
    ("Rib-Knit Mini Shorts Red",24.99,"red","Shorts","casual","https://www2.hm.com/en_ca/productpage.1340105002.html","https://image.hm.com/assets/hm/01/be/01bec43a886f52f7e9e9dda671648e2178b978d0.jpg?imwidth=1536"),
    ("Rib-Knit Mini Shorts Yellow",24.99,"yellow","Shorts","casual","https://www2.hm.com/en_ca/productpage.1340105001.html","https://image.hm.com/assets/hm/61/47/614782918de031a7c39ba61f5fa3877b6fec4132.jpg?imwidth=1536"),
    ("Oversized Nylon Anorak",34.99,"red","Jacket","sporty","https://www2.hm.com/en_ca/productpage.1340637001.html","https://image.hm.com/assets/hm/b5/a0/b5a064ee07661dd34e54371507d79a94aa8639a5.jpg?imwidth=1536"),
    ("Flounce-Trimmed Lace Blouse",24.99,"beige","Shirt","casual","https://www2.hm.com/en_ca/productpage.1341100001.html","https://image.hm.com/assets/hm/c2/63/c26335b7dd2e6537219411aab3692d0f11aa0efd.jpg?imwidth=1536"),
    ("Split Suede Loafers",24.99,"brown","Flats","casual","https://www2.hm.com/en_ca/productpage.1323549002.html","https://image.hm.com/assets/hm/76/fd/76fdfb133947267d0c225e72564f07444487c83a.jpg?imwidth=1536"),
]:
    products.append({"name":name,"brand":"H&M","cat":cat,"color":color,"style":style,"price":str(price),"image_url":img,"url":url})

# ── Generate SQL ──
lines = [
    "-- Auto-generated product seed data from real Canadian store scraping",
    "-- Generated: 2026-04-06",
    "-- Sources: H&M Canada, UNIQLO Canada, ZARA Canada, Roots Canada, Oak+Fort, Aritzia",
    "",
    "-- Clear existing products",
    "DELETE FROM products;",
    "",
    "-- Insert scraped products with real images, prices, and URLs",
]

# Filter out products with transparent images
valid = [p for p in products if TRANSPARENT not in (p.get('image_url') or '')]
print(f"Total valid products: {len(valid)}")

for i, p in enumerate(valid):
    price = parse_price(p['price'])
    name = esc(p['name'])
    brand = esc(p['brand'])
    cat = esc(p['cat'])
    color = esc(p['color'])
    style = esc(p['style'])
    img = esc(p['image_url'])
    url = esc(p['url'])

    lines.append(
        f"INSERT INTO products (name, brand, category, color, style, price, image_url, affiliate_url) "
        f"VALUES ('{name}', '{brand}', '{cat}', '{color}', '{style}', {price}, '{img}', '{url}');"
    )

sql = '\n'.join(lines) + '\n'
with open('/Users/parkyoungbin/Documents/personal_project/codi/supabase/seed_products_v2.sql', 'w') as f:
    f.write(sql)
print(f"Written to seed_products_v2.sql")
