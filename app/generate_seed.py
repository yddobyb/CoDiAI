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
    ("AIRism Cotton T-Shirt",19.90,"white","https://www.uniqlo.com/ca/en/products/E465293-000/00","https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/465293/item/cagoods_01_465293_3x4.jpg?width=300"),
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
    ("ZW Collection Poplin Bib Shirt",79.90,"white","https://www.zara.com/ca/en/zw-collection-poplin-bib-shirt-p06097362.html","https://static.zara.net/assets/public/b3a6/7130/6e184b126940/2a6158175883/06097362000-000-f1/06097362000-000-f1.jpg?ts=1775136880552&w=1769"),
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
    ("Braided Effect Flat Ballet Flats",69.90,"beige","Flats","https://www.zara.com/ca/en/braided-effect-flat-ballet-flats-p13521710.html","https://static.zara.net/assets/public/b5bf/b7ec/6ac54d568d8c/315ff626d165/13521710098-ult41/13521710098-ult41.jpg?ts=1772723563656&w=1809"),
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

# Aritzia Sweater
products.append({"name":"Golightly Cardigan","brand":"Aritzia","cat":"Sweater","color":"beige","style":"casual","price":"118.00","image_url":"https://assets.aritzia.com/image/upload/c_crop,ar_1920:2623,g_south/q_auto,f_auto,dpr_auto/s26_a03_132752_4425_on_d","url":"https://www.aritzia.com/en/product/golightly-cardigan/114360.html"})

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
