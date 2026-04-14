#!/usr/bin/env python3
"""
Upload Firecrawl-scraped products to Supabase.

Processes raw data from Garage, Dynamite, Lululemon, Aritzia, Zara, Uniqlo.
Normalizes, deduplicates, and batch-inserts.

Usage:
    python upload_firecrawl.py              # Upload to Supabase
    python upload_firecrawl.py --dry-run    # Preview without uploading
    python upload_firecrawl.py --output x.json  # Export to JSON
"""

import argparse
import json
import sys
from collections import Counter

sys.path.insert(0, ".")
from normalize import normalize_product

from config import SUPABASE_URL, SUPABASE_KEY

# ── Raw scraped data from Firecrawl ──

GARAGE_RAW = [
    {"name": "UltraFleece Hoodie", "price": "69.95", "color": "Jet Black", "image_url": "https://dam.dynamiteclothing.com/m/1b5de46cb4e2825e/original/100092201_08L_1920x2880.jpg?sw=200&sh=300", "affiliate_url": "https://www.garageclothing.com/ca/p/ultrafleece-hoodie/10009220108L.html"},
    {"name": "UltraFleece Hoodie", "price": "69.95", "color": "Electric Blue", "image_url": "https://dam.dynamiteclothing.com/asset/2fda2f21-731c-4f25-a07b-534abe026508/100092201_01G_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/ultrafleece-hoodie/10009220101G.html"},
    {"name": "Oversized Faux Leather Stand Collar Bomber", "price": "119.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/3d71f9a649ed5005/original/100102698_7NK_1920x2880.jpg?sw=200&sh=300", "affiliate_url": "https://www.garageclothing.com/ca/p/oversized-faux-leather-stand-collar-bomber/1001026987NK.html"},
    {"name": "Snatch Booty StretchTerry Pants", "price": "64.95", "color": "Pop It Pink", "image_url": "https://dam.dynamiteclothing.com/asset/3f3661e9-fa5e-410c-9ea6-322c44c5d8d8/100102968_8KV_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/snatch-booty-stretchterry-pants/1001029688KV.html"},
    {"name": "UltraFleece Wide Leg Sweatpants", "price": "64.95", "color": "Spring Grey", "image_url": "https://dam.dynamiteclothing.com/asset/8ab303be-0818-4569-bf29-603caaba6dd5/100105054_18X_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/ultrafleece-wide-leg-sweatpants/10010505418X.html"},
    {"name": "UltraFleece Wide Leg Sweatpants", "price": "64.95", "color": "Armadillo Brown", "image_url": "https://dam.dynamiteclothing.com/asset/598a0c20-8b7a-4cb6-b48d-a2ce15b12edf/100105054_4DD_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/ultrafleece-wide-leg-sweatpants/1001050544DD.html"},
    {"name": "Perfect Peach Active Pants", "price": "69.95", "color": "Satellite Beige", "image_url": "https://dam.dynamiteclothing.com/m/352ef6305026c085/original/100104461_3HS_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/perfect-peach-active-pants/1001044613HS.html"},
    {"name": "Perfect Peach Active Pants", "price": "69.95", "color": "Coconut Whip Beige", "image_url": "https://dam.dynamiteclothing.com/m/6c2a9291e25dd7c5/original/100104940_8MS_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/perfect-peach-active-pants/1001049408MS.html"},
    {"name": "StretchTerry Cheeky Shorts", "price": "39.95", "color": "Spring Grey", "image_url": "https://dam.dynamiteclothing.com/m/794884decaea3638/original/100105612_18X_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/stretchterry-cheeky-shorts/10010561218X.html"},
    {"name": "Active Layered Tank Top", "price": "49.95", "color": "Beige", "image_url": "https://dam.dynamiteclothing.com/m/7438d85085126a77/original/100103452_8NN_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/active-layered-tank-top/1001034528NN.html"},
    {"name": "Active Plunge Cami Top", "price": "44.95", "color": "Pink", "image_url": "https://dam.dynamiteclothing.com/m/c5e30e73-cef3-4289-96f0-e938b083fa07/100103895_8MS_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/active-plunge-cami-top/1001038958MS.html"},
    {"name": "Sleek Plunge Adjustable Halter Top", "price": "32.95", "color": "Electric Blue", "image_url": "https://dam.dynamiteclothing.com/m/5f71da816a58814/original/100103558_08L_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/sleek-plunge-adjustable-halter-top/10010355808L.html"},
    {"name": "SoftTerry Off Shoulder Sweatshirt", "price": "59.95", "color": "Burnt Ash Grey", "image_url": "https://dam.dynamiteclothing.com/asset/6210b807-f633-4a5a-bc46-f0215a3e9170/100097132_8D1_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/softterry-off-shoulder-sweatshirt/1000971328D1.html"},
    {"name": "Cropped Button Up Top", "price": "44.95", "color": "Spring Grey", "image_url": "https://dam.dynamiteclothing.com/asset/1b5a7856-5ac3-481b-95ee-3e761388fbec/100104499_18X_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/cropped-button-up-top/10010449918X.html"},
    {"name": "Sleek Plunge T-Shirt", "price": "36.95", "color": "Pink", "image_url": "https://dam.dynamiteclothing.com/m/639392d80e19eea7/original/100104898_8NA_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/sleek-plunge-t-shirt/1001048988NA.html"},
    {"name": "UltraFleece Barrel Leg Sweatpants", "price": "64.95", "color": "Satellite Beige", "image_url": "https://dam.dynamiteclothing.com/asset/0565256f-fff7-498b-a30a-7b5dc7dedd26/100103312_3HS_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/ultrafleece-barrel-leg-sweatpants/1001033123HS.html"},
    {"name": "Sleek Scoop Cami Top", "price": "26.95", "color": "Pink", "image_url": "https://dam.dynamiteclothing.com/m/1d97a56fe874dbdd/original/100092730_8OZ_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/sleek-scoop-cami-top/1000927308OZ.html"},
    {"name": "Low Rise Baggy Jeans", "price": "74.95", "color": "Bright White", "image_url": "https://dam.dynamiteclothing.com/asset/844986f4-3201-498d-95ea-43a8cd7582c8/100102281_07S_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/low-rise-baggy-jeans/10010228107S.html"},
    {"name": "Low Rise Relaxed Jeans", "price": "74.95", "color": "Jet Black", "image_url": "https://dam.dynamiteclothing.com/asset/acd2d2f6-0003-451c-8ecc-5ef42dc656b6/100105498_07I_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/low-rise-relaxed-jeans/10010549807I.html"},
    {"name": "Low Rise Bodycon Denim Skort", "price": "54.95", "color": "Claire Blue", "image_url": "https://dam.dynamiteclothing.com/m/506be6eedeb45303/original/100102656_07H_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/low-rise-bodycon-denim-skort/10010265607H.html"},
    {"name": "High Rise Wide Leg Jeans", "price": "74.95", "color": "Britt Blue", "image_url": "https://dam.dynamiteclothing.com/asset/61f14c48-7cc2-4176-8591-d4c2b200056f/100104092_07I_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/high-rise-wide-leg-jeans/10010409207I.html"},
    {"name": "High Rise Cheeky Denim Shorts", "price": "59.95", "color": "Serena Blue", "image_url": "https://dam.dynamiteclothing.com/m/7afc976552ec71c5/original/100104162_07H_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/high-rise-cheeky-denim-shorts/10010416207H.html"},
    {"name": "Low Rise Cuffed Denim Shorts", "price": "59.95", "color": "Blue", "image_url": "https://dam.dynamiteclothing.com/m/2342ce35d8933ac2/original/100104573_07J_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/low-rise-cuffed-denim-shorts/10010457307J.html"},
    {"name": "Denim Relaxed A-Line Shorts", "price": "59.95", "color": "Indigo Dark", "image_url": "https://dam.dynamiteclothing.com/m/75e07ea6d34d9d04/original/100101199_07L_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/denim-relaxed-a-line-shorts/10010119907L.html"},
    {"name": "Denim Festival Shorts", "price": "59.95", "color": "Ink Black", "image_url": "https://dam.dynamiteclothing.com/m/5b6c4197fca28d96/original/100101192_07J_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.garageclothing.com/ca/p/denim-festival-shorts/10010119207J.html"},
]

DYNAMITE_RAW = [
    {"name": "Rebecca Crewneck Cardigan", "price": "59.95", "color": "Beige", "image_url": "https://dam.dynamiteclothing.com/m/500caed5f477851a/original/100094919_0ED_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/rebecca-crewneck-cardigan/1000949190ED.html"},
    {"name": "Charlotte Short Faux Leather Jacket", "price": "99.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/44d51e167267c049/original/100099825_06V_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/charlotte-short-faux-leather-jacket/10009982506V.html"},
    {"name": "Nola Sculpt Tank Top", "price": "34.95", "color": "Grey", "image_url": "https://dam.dynamiteclothing.com/m/2993395dc00e7c23/original/100095375_1MG_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/nola-sculpt-tank-top/1000953751MG.html"},
    {"name": "Madi Lace Satin Cami Top", "price": "59.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/e39ac92b6d04b9c/original/100102366_06V_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/madi-lace-satin-cami-top/10010236606V.html"},
    {"name": "Polo Cardigan", "price": "54.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/203ff752b504ab6/original/100100564_0NO_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/polo-cardigan/1001005640NO.html"},
    {"name": "Lace Halter Top", "price": "44.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/532dc2d164bc6a43/original/100103984_06V_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/lace-halter-top/10010398406V.html"},
    {"name": "Everyday Cotton T Shirt", "price": "34.95", "color": "White", "image_url": "https://dam.dynamiteclothing.com/m/7ff4935366bd8c8d/original/100096349_8FU_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/everyday-cotton-t-shirt/1000963498FU.html"},
    {"name": "Isla Oversized Linen Shirt", "price": "69.95", "color": "Beige", "image_url": "https://dam.dynamiteclothing.com/m/62c19814f9b83515/original/100102971_8HM_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/isla-oversized-linen-shirt/1001029718HM.html"},
    {"name": "Clara Short Sleeve Sweater", "price": "44.95", "color": "Beige", "image_url": "https://dam.dynamiteclothing.com/m/211441d09ac3c37b/original/100103025_0ED_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/clara-short-sleeve-sweater/1001030250ED.html"},
    {"name": "Gemma Poplin Halter Top", "price": "49.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/6bd541b4c2412c8a/original/100099842_0NO_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/gemma-poplin-halter-top/1000998420NO.html"},
    {"name": "Rumi Crewneck T Shirt", "price": "34.95", "color": "Green", "image_url": "https://dam.dynamiteclothing.com/asset/8fe0199a-b1c0-45e5-b7da-3615955c42df/100099624_6QE_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/rumi-crewneck-t-shirt/1000996246QE.html"},
    {"name": "Scallop Trim Sweater Halter Top", "price": "49.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/5ccaef0dcf9bd8aa/original/100102587_06V_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/scallop-trim-sweater-halter-top/10010258706V.html"},
    {"name": "Sculpt Cowl Back Bodysuit", "price": "44.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/370dd735b61cc06b/original/100098963_06V_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/sculpt-cowl-back-bodysuit/10009896306V.html"},
    {"name": "Boat Neck Sweater", "price": "49.95", "color": "Beige", "image_url": "https://dam.dynamiteclothing.com/asset/2517aee5-d2a8-4935-9821-710f6e913ab3/100101674_0E6_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/boat-neck-sweater-/1001016740E6.html"},
    {"name": "Turtleneck Sweater Tank Top", "price": "44.95", "color": "Brown", "image_url": "https://dam.dynamiteclothing.com/asset/3a3b36c5-8d69-43be-81ca-aed8d99f7b8c/100104144_7TL_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/turtleneck-sweater-tank-top/1001041447TL.html"},
    {"name": "Nola Sculpt Tank Top", "price": "34.95", "color": "Pink", "image_url": "https://dam.dynamiteclothing.com/m/985b389670418d6/original/100095375_08R_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/nola-sculpt-tank-top/10009537508R.html"},
    {"name": "Iris Ponte Maxi Dress", "price": "139.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/593b99a15618733/original/100096517_0NO_1920x2880.jpg?sw=200&sh=300", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/iris-ponte-maxi-dress/1000965170NO.html"},
    {"name": "Ruffle Maxi Dress", "price": "119.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/35bb9df3e7734093/original/100103602_06V_1920x2880.jpg?sw=200&sh=300", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/ruffle-maxi-dress/10010360206V.html"},
    {"name": "Taylor Poplin Maxi Dress", "price": "119.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/593b99a15618733/original/100096555_0NO_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/taylor-poplin-maxi-dress/1000965550NO.html"},
    {"name": "Celia Sculpt Mini Dress", "price": "104.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/35bb9df3e7734093/original/10010374506V_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/celia-sculpt-mini-dress/10010374506V.html"},
    {"name": "Mona Mesh Maxi Dress", "price": "119.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/35bb9df3e7734093/original/1001022258KN_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/mona-mesh-maxi-dress/1001022258KN.html"},
    {"name": "Jayde Stretch Satin Maxi Dress", "price": "129.95", "color": "Beige", "image_url": "https://dam.dynamiteclothing.com/m/35bb9df3e7734093/original/1001002440E6_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/jayde-stretch-satin-maxi-dress/1001002440E6.html"},
    {"name": "Fitted Mini Skort", "price": "59.95", "color": "Java Brown", "image_url": "https://dam.dynamiteclothing.com/asset/1b83c2bc-bea7-4632-89d1-022dfc461589/100102478_7GM_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/fitted-mini-skort/1001024787GM.html"},
    {"name": "Stacie Mini Skort", "price": "59.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/asset/142e75f4-86db-4ade-ab4f-f4cd31958b17/100102732_06V_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/stacie-mini-skort/10010273206V.html"},
    {"name": "Stacie Linen Mini Skort", "price": "59.95", "color": "White", "image_url": "https://dam.dynamiteclothing.com/asset/3859e020-ddfb-47b7-840e-f540c386651a/100103201_03G_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/stacie-linen-mini-skort/10010320103G.html"},
    {"name": "Scallop Trim Maxi Skirt", "price": "59.95", "color": "Blue", "image_url": "https://dam.dynamiteclothing.com/m/a50443f1ce33087/original/100104460_0NO_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/scallop-trim-maxi-skirt/1001044600NO.html"},
    {"name": "Delila Satin Midi Skirt", "price": "64.95", "color": "White", "image_url": "https://dam.dynamiteclothing.com/m/6fd7bd85c2cc3f5f/original/100102096_0QO_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/delila-satin-midi-skirt/1001020960QO.html"},
    {"name": "Structured Faux Leather Midi Skirt", "price": "79.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/5746a5d1b7b1a674/original/100103866_06V_1920x2880.jpg?sw=320&sh=480", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/structured-faux-leather-midi-skirt/10010386606V.html"},
    {"name": "Alex Anywear Wide Leg Pants", "price": "69.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/14df7b85228873f/original/100099002_06V_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/alex-anywear-wide-leg-pants/10009900206V.html"},
    {"name": "High Rise Slim Bootcut Pants", "price": "79.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/4e13d37e2c4e44e1/original/100103200_06V_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/high-rise-slim-bootcut-pants/10010320006V.html"},
    {"name": "Izzy Wide Leg Satin Pants", "price": "79.95", "color": "White", "image_url": "https://dam.dynamiteclothing.com/m/19be07b5cbc5b26f/original/100101041_0QO_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/izzy-wide-leg-satin-pants/1001010410QO.html"},
    {"name": "Leo Linen Wide Leg Pants", "price": "79.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/68c7c2b4ef4a7c7f/original/100102800_06V_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/leo-linen-wide-leg-pants/10010280006V.html"},
    {"name": "Priya Wide Leg Pants", "price": "69.95", "color": "White", "image_url": "https://dam.dynamiteclothing.com/m/593616f6e4d6ae1a/original/100103980_8J3_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/priya-wide-leg-pants/1001039808J3.html"},
    {"name": "Alex Airflow Wide Leg Pants", "price": "79.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/1d645bcc46a8d33f/original/100102723_39C_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/alex-airflow-wide-leg-pants/10010272339C.html"},
    {"name": "Yasmin Airflow Straight Leg Pants", "price": "79.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/2d70f584118bd645/original/100098679_06V_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/yasmin-airflow-straight-leg-pants/10009867906V.html"},
    {"name": "Frankie Tailored Slim Bootcut Pants", "price": "79.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/2b0fcb856bead5d6/original/100102733_06V_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/frankie-tailored-slim-bootcut-pants/10010273306V.html"},
    {"name": "Satin Balloon Pants", "price": "79.95", "color": "Black", "image_url": "https://dam.dynamiteclothing.com/m/428c952435839640/original/100102347_06V_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/satin-balloon-pants/10010234706V.html"},
    {"name": "Leo Airflow Wide Leg Pants", "price": "79.95", "color": "Beige", "image_url": "https://dam.dynamiteclothing.com/m/326906499d8285c8/original/100101949_3XD_1920x2880.jpg", "affiliate_url": "https://www.dynamiteclothing.com/ca/p/leo-airflow-wide-leg-pants/1001019493XD.html"},
]

LULULEMON_RAW = [
    {"name": "Flow Y Bra Nulu Light Support", "price": "48", "color": "Blue", "image_url": "https://images.lululemon.com/is/image/lululemon/73715", "affiliate_url": "https://shop.lululemon.com/p/women-sports-bras/Flow-Y-Bra-Nulu/_/prod8910081"},
    {"name": "Align High-Rise Pant 25", "price": "118", "color": "Blue", "image_url": "https://images.lululemon.com/is/image/lululemon/46927", "affiliate_url": "https://shop.lululemon.com/p/womens-leggings/Align-Pant-2/_/prod2020012"},
    {"name": "Align Side-Slit Skirt", "price": "78", "color": "Pink", "image_url": "https://images.lululemon.com/is/image/lululemon/74133", "affiliate_url": "https://shop.lululemon.com/p/lululemon-align-side-slit-skirt-trim/f06y18jng0"},
    {"name": "Define Jacket Nulu", "price": "128", "color": "Blue", "image_url": "https://images.lululemon.com/is/image/lululemon/74050", "affiliate_url": "https://shop.lululemon.com/p/jackets-and-hoodies-jackets/Define-Jacket-Nulu/_/prod11020158"},
    {"name": "Define Cropped Jacket Nulu", "price": "128", "color": "Lavender", "image_url": "https://images.lululemon.com/is/image/lululemon/76047", "affiliate_url": "https://shop.lululemon.com/p/jackets-and-hoodies-jackets/Nulu-Cropped-Define-Jacket/_/prod10930188"},
    {"name": "Scuba Oversized Dolphin-Hem Short", "price": "78", "color": "Pink", "image_url": "https://images.lululemon.com/is/image/lululemon/74020", "affiliate_url": "https://shop.lululemon.com/p/scuba-oversized-mid-rise-dolphin-hem-short-3-wash/gjms9tlz3r"},
    {"name": "Mist Over Windbreaker", "price": "128", "color": "Green", "image_url": "https://images.lululemon.com/is/image/lululemon/74049", "affiliate_url": "https://shop.lululemon.com/p/jackets-and-hoodies-jackets/Mist-Over-Windbreaker/_/prod9270522"},
    {"name": "Align Dress Updated Sleek Liner", "price": "148", "color": "White", "image_url": "https://images.lululemon.com/is/image/lululemon/74046", "affiliate_url": "https://shop.lululemon.com/p/skirts-and-dresses-dresses/lululemon-Align-Dress-Updated-Sleek-Liner/_/prod20002931"},
    {"name": "Hotty Hot High-Rise Lined Short", "price": "68", "color": "White", "image_url": "https://images.lululemon.com/is/image/lululemon/74046", "affiliate_url": "https://shop.lululemon.com/p/women-shorts/Hotty-Hot-Short-HR/_/prod9250076"},
]

ARITZIA_RAW = [
    {"name": "FigureKnit Priestly Dress", "price": "138", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131184_36523_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/figureknit-priestly-dress/130737.html"},
    {"name": "Encourage Poplin Dress", "price": "168", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131094_11420_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/encourage-poplin-dress/131094.html"},
    {"name": "Intimo Dress", "price": "128", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131471_11524_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/intimo-dress/131471.html"},
    {"name": "Grazie Dress", "price": "158", "color": "Beige", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131317_36524_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/grazie-dress/131317.html"},
    {"name": "Altura Poplin Dress", "price": "148", "color": "Green", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131731_36527_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/altura-poplin-dress/131731.html"},
    {"name": "Fresca Dress", "price": "148", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131316_11420_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/fresca-dress/131316.html"},
    {"name": "Tina Poplin Dress", "price": "168", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131097_1274_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/tina-poplin-dress/131097.html"},
    {"name": "Eleta Poplin Maxi Dress", "price": "168", "color": "Blue", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_130120_36771_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/eleta-poplin-maxi-dress/130120.html"},
    {"name": "Celebrate Dress", "price": "168", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_119390_1274_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/celebrate-dress/119390.html"},
    {"name": "Encino Dress", "price": "148", "color": "Blue", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131727_36523_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/encino-dress/131727.html"},
    {"name": "Mastermind Dress", "price": "168", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_119391_1274_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/mastermind-dress/119391.html"},
    {"name": "Revive Poplin Dress", "price": "148", "color": "White", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_131034_27400_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/revive-poplin-dress/131034.html"},
    {"name": "Dollop Dress", "price": "128", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_126968_1274_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/dollop-dress/126968.html"},
    {"name": "Mason Poplin Dress", "price": "138", "color": "Blue", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_119645_36342_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/mason-poplin-dress/119645.html"},
    {"name": "Lilt Dress", "price": "168", "color": "Black", "image_url": "https://assets.aritzia.com/image/upload/v1680000000/s26_a08_130621_6445_on_a.jpg", "affiliate_url": "https://www.aritzia.com/us/en/product/lilt-dress/130621.html"},
]

ZARA_RAW = [
    {"name": "Asymmetrical Ruffled Dress", "price": "69.90", "color": "Cream", "image_url": "https://static.zara.net/assets/public/2664/2bcd/7bf647aa983a/1b6ca5871524/7246b83f6aa07de8dc2b2a012170a39c/7246b83f6aa07de8dc2b2a012170a39c.jpg?ts=1775470278700&w=1809", "affiliate_url": "https://www.zara.com/ca/en/asymmetric-ruffled-dress---the-item-p02283135.html"},
    {"name": "Sequin Flowy Pants", "price": "59.90", "color": "Black", "image_url": "https://static.zara.net/assets/public/f412/c7ed/8f954ea9ae74/ad1dba186fb3/844790df8083e065fdbcbc45c89d0eda/844790df8083e065fdbcbc45c89d0eda.jpg?ts=1775807617685&w=1809", "affiliate_url": "https://www.zara.com/ca/en/sequin-flowy-pants-p02422929.html"},
    {"name": "Sequin Double Breasted Blazer", "price": "119", "color": "Brown", "image_url": "https://static.zara.net/assets/public/e123/6cf0/9dcf46758d8f/d14ef0eab701/ba4a29e455d4251d9d859072e2fba970/ba4a29e455d4251d9d859072e2fba970.jpg?ts=1775807617117&w=1809", "affiliate_url": "https://www.zara.com/ca/en/sequin-double-breasted-blazer-p02423929.html"},
    {"name": "Rustic Lace Insert Blouse", "price": "49.90", "color": "Beige", "image_url": "https://static.zara.net/assets/public/0688/7e4d/c5f7490dba2a/bb6ec81c1c23/08741037746-h1/08741037746-h1.jpg?ts=1775748439271&w=1809", "affiliate_url": "https://www.zara.com/ca/en/rustic-lace-insert-blouse-p08741037.html"},
    {"name": "Lace Knotted Skort", "price": "49.90", "color": "Beige", "image_url": "https://static.zara.net/assets/public/70dd/3fd4/81784e9a863f/48d8deebd479/08741058746-a2/08741058746-a2.jpg?ts=1775748440984&w=1809", "affiliate_url": "https://www.zara.com/ca/en/lace-knotted-skort-p08741058.html"},
    {"name": "Embroidered Top with Side Laces", "price": "59.90", "color": "White", "image_url": "https://static.zara.net/assets/public/5f98/e6f4/65494310a54c/d99afc8bf16b/07200024712-a2/07200024712-a2.jpg?ts=1775748397237&w=1809", "affiliate_url": "https://www.zara.com/ca/en/embroidered-top-with-side-laces-p07200024.html"},
    {"name": "Knitted Midi Skirt", "price": "59.90", "color": "Sand", "image_url": "https://static.zara.net/assets/public/1bdd/eb44/c27447aebbc6/cd109b29f0e8/02756033711-a2/02756033711-a2.jpg?ts=1775748337081&w=1809", "affiliate_url": "https://www.zara.com/ca/en/knit-midi-skirt-p02756033.html"},
    {"name": "Striped Bubble Midi Dress", "price": "69.90", "color": "Black", "image_url": "https://static.zara.net/assets/public/3020/3eab/32ae414188af/df37122f6b69/04387034070-a1/04387034070-a1.jpg?ts=1775748356013&w=1809", "affiliate_url": "https://www.zara.com/ca/en/striped-bubble-midi-dress-p04387034.html"},
    {"name": "Embroidered Poplin Mini Dress", "price": "69.90", "color": "Brown", "image_url": "https://static.zara.net/assets/public/b92d/cdc5/dcd8482cb49e/5c10737360df/05770052700-p/05770052700-p.jpg?ts=1775748385638&w=1809", "affiliate_url": "https://www.zara.com/ca/en/embroidered-poplin-mini-dress-p05770052.html"},
    {"name": "Fringed Crop Top", "price": "49.90", "color": "Brown", "image_url": "https://static.zara.net/assets/public/265c/081d/14224e828aa2/86cebcc448c6/08372129700-h1/08372129700-h1.jpg?ts=1775748427230&w=1809", "affiliate_url": "https://www.zara.com/ca/en/fringed-crop-top-p08372129.html"},
    {"name": "Embroidered Eyelet Midi Dress", "price": "119", "color": "Pink", "image_url": "https://static.zara.net/assets/public/e75f/38fa/49e8420b81cb/96784efc7d54/02715977620-a2/02715977620-a2.jpg?ts=1775808763197&w=1809", "affiliate_url": "https://www.zara.com/ca/en/embroidered-eyelet-midi-dress-p02715977.html"},
    {"name": "Poplin Tie Midi Dress", "price": "69.90", "color": "Pink", "image_url": "https://static.zara.net/assets/public/dcdc/1962/f4924510b6d2/22128137259c/05029241645-p/05029241645-p.jpg?ts=1775808799376&w=1809", "affiliate_url": "https://www.zara.com/ca/en/poplin-midi-dress-with-ties-p05029241.html"},
    {"name": "ZW Collection Halter Polka Dot Dress", "price": "99.90", "color": "Brown", "image_url": "https://static.zara.net/assets/public/d943/355b/8c7b47bd912a/811e479866f0/04437042087-p/04437042087-p.jpg?ts=1775723677752&w=1809", "affiliate_url": "https://www.zara.com/ca/en/zw-collection-halter-polka-dot-dress-p04437042.html"},
    {"name": "ZW Collection Linen Blend Midi Dress", "price": "99.90", "color": "Beige", "image_url": "https://static.zara.net/assets/public/4ef7/5219/c0804d28b420/e304594fe2d0/05289025620-a2/05289025620-a2.jpg?ts=1775059694704&w=1809", "affiliate_url": "https://www.zara.com/ca/en/zw-collection-linen-blend-midi-dress-p05289025.html"},
    {"name": "TRF Denim Mini Dress", "price": "55.90", "color": "Blue", "image_url": "https://static.zara.net/assets/public/d83e/632b/a3524d07b634/17b0fc7700c5/05252081401-p/05252081401-p.jpg?ts=1774970871824&w=1809", "affiliate_url": "https://www.zara.com/ca/en/trf-denim-mini-dress-p05252081.html"},
    {"name": "Floral Halter Neck Mini Dress", "price": "55.90", "color": "Red", "image_url": "https://static.zara.net/assets/public/d050/4528/16434598bb97/7699ed6d8c52/02743300600-p/02743300600-p.jpg?ts=1774970852525&w=1809", "affiliate_url": "https://www.zara.com/ca/en/floral-halter-mini-dress-p02743300.html"},
    {"name": "Ruffled Short Dress", "price": "65.90", "color": "Brown", "image_url": "https://static.zara.net/assets/public/ba87/5fcc/cccd440cb724/4d40549747d5/00881307904-a5/00881307904-a5.jpg?ts=1772186706821&w=1809", "affiliate_url": "https://www.zara.com/ca/en/ruffled-short-dress-p00881307.html"},
    {"name": "Sweetheart Neckline Dress", "price": "69.90", "color": "Black", "image_url": "https://static.zara.net/assets/public/a0fa/bef1/46de4df8bfa4/2f74d3e419cc/01058006800-p/01058006800-p.jpg?ts=1773398902041&w=1809", "affiliate_url": "https://www.zara.com/ca/en/sweetheart-neckline-dress-p01058006.html"},
    {"name": "Belted Striped Halter Dress", "price": "45.90", "color": "Brown", "image_url": "https://static.zara.net/assets/public/c548/18a7/51ed44d0a449/a505255e5933/05063353178-a4/05063353178-a4.jpg?ts=1775052055446&w=1809", "affiliate_url": "https://www.zara.com/ca/en/striped-halter-dress-with-belt-p05063353.html"},
    {"name": "Jacquard Balloon Mini Dress", "price": "79.90", "color": "White", "image_url": "https://static.zara.net/assets/public/1341/6bc5/67ce4410be1d/9ebfceb4991a/04813319321-a6/04813319321-a6.jpg?ts=1773257143718&w=1809", "affiliate_url": "https://www.zara.com/ca/en/jacquard-balloon-mini-dress-p01165074.html"},
    {"name": "TRF High Waist Wide Leg Jeans", "price": "65.90", "color": "Black", "image_url": "https://static.zara.net/assets/public/54a5/62b1/06244f9ba703/c53d202aac11/f4f2062fc8b860126dc3fe05039684aa/f4f2062fc8b860126dc3fe05039684aa.jpg?ts=1775045503495&w=1809", "affiliate_url": "https://www.zara.com/ca/en/trf-high-waist-wide-leg-jeans-p05575229.html"},
    {"name": "Z1975 Hi-Rise Front Seam Jeans", "price": "65.90", "color": "Blue", "image_url": "https://static.zara.net/assets/public/12df/a580/5f78488dacea/25d272ea16e6/c09ea01c56eb7718695290f8717c7f6d/c09ea01c56eb7718695290f8717c7f6d.jpg?ts=1775749767587&w=1809", "affiliate_url": "https://www.zara.com/ca/en/z1975-high-waisted-front-seam-jeans-p09942068.html"},
    {"name": "Z1975 High-Waist Mom Fit Jeans", "price": "55.90", "color": "Blue", "image_url": "https://static.zara.net/assets/public/b1a8/9b53/af2d4c6786ff/a27414e403d9/7588fddd0098c603b319f0661c13038e/7588fddd0098c603b319f0661c13038e.jpg?ts=1775042074961&w=1809", "affiliate_url": "https://www.zara.com/ca/en/z-05-high-waist-mom-fit-jeans-p04083022.html"},
    {"name": "TRF Mid-Rise Balloon Jeans", "price": "65.90", "color": "Blue", "image_url": "https://static.zara.net/assets/public/9572/72ce/1ad7499da7a3/c2f9d8c474c3/f0c0542b47f1c58acdfd7a5070802275/f0c0542b47f1c58acdfd7a5070802275.jpg?ts=1775683046313&w=1809", "affiliate_url": "https://www.zara.com/ca/en/trf-mid-rise-balloon-jeans-p06929052.html"},
    {"name": "Linen Pocket Shirt", "price": "69.90", "color": "Pink", "image_url": "https://static.zara.net/assets/public/4cb2/80a5/dfe6490eaa59/7c2643bcf859/05344010619-p/05344010619-p.jpg?ts=1774949608365&w=1809", "affiliate_url": "https://www.zara.com/ca/en/zw-collection-linen-pocket-shirt-p05344010.html"},
    {"name": "Oversized Gauze Shirt with Pocket", "price": "39.90", "color": "Yellow", "image_url": "https://static.zara.net/assets/public/2c90/1fda/f5ad4cb78d0b/5c0c1f32805f/07521002306-f1/07521002306-f1.jpg?ts=1774617411449&w=1769", "affiliate_url": "https://www.zara.com/ca/en/oversized-gauze-shirt-with-pocket-p07521002.html"},
    {"name": "Striped Cotton Shirt", "price": "45.90", "color": "White", "image_url": "https://static.zara.net/assets/public/e8e7/d756/9f494c4f9538/1c0a52b986a1/02157046250-f1/02157046250-f1.jpg?ts=1770801277788&w=1769", "affiliate_url": "https://www.zara.com/ca/en/striped-cotton-shirt-p02157046.html"},
    {"name": "Pleated Poplin Shirt", "price": "55.90", "color": "White", "image_url": "https://static.zara.net/assets/public/6342/f09b/632b4b8fb2df/a4f944c3e6b2/02110340250-f1/02110340250-f1.jpg?ts=1769013562766&w=1769", "affiliate_url": "https://www.zara.com/ca/en/pleated-poplin-shirt-p02110340.html"},
    {"name": "Embroidered Blouse", "price": "45.90", "color": "White", "image_url": "https://static.zara.net/assets/public/9056/f0b9/5da44efdb31c/ac7d98f56530/08741022250-000-f1/08741022250-000-f1.jpg?ts=1772009957363&w=1769", "affiliate_url": "https://www.zara.com/ca/en/embroidered-blouse-p08741022.html"},
    {"name": "Basic Poplin Shirt", "price": "45.90", "color": "White", "image_url": "https://static.zara.net/assets/public/0724/6801/3c22442eb435/0dd16564f764/00387060250-f1/00387060250-f1.jpg?ts=1774347733078&w=1769", "affiliate_url": "https://www.zara.com/ca/en/basic-poplin-shirt-p00387060.html"},
]

UNIQLO_RAW = [
    {"name": "Mini Short Sleeve T-Shirt", "price": "19.90", "color": "Black", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/465760/item/cagoods_00_465760_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E465760-000"},
    {"name": "Mini Polo Shirt", "price": "29.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/476068/item/cagoods_51_476068_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E476068-000"},
    {"name": "Ribbed Mini T-Shirt", "price": "19.90", "color": "Pink", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484457/item/cagoods_09_484457_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E484457-000"},
    {"name": "Washed Cotton Boxy T-Shirt", "price": "19.90", "color": "Beige", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483596/item/cagoods_03_483596_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E483596-000"},
    {"name": "AIRism Cotton Short Sleeve T-Shirt", "price": "19.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/465755/item/cagoods_54_465755_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E465755-000"},
    {"name": "Crew Neck T-Shirt", "price": "19.90", "color": "Black", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/424873/item/cagoods_00_424873_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E424873-000"},
    {"name": "Supima Cotton T-Shirt", "price": "14.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483461/item/cagoods_73_483461_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E483461-000"},
    {"name": "Sweat Full Zip Hoodie", "price": "39.90", "color": "Black", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484236/item/cagoods_60_484236_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E484236-000"},
    {"name": "Fluffy Yarn Fleece Full-Zip Jacket", "price": "49.90", "color": "Pink", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/449753/item/cagoods_36_449753_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E449753-000"},
    {"name": "Racer Back Bra Top", "price": "34.90", "color": "Black", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482839/item/cagoods_10_482839_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482839-000"},
    {"name": "Baggy Jeans", "price": "59.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483999/item/cagoods_67_483999_3x4.jpg?width=200", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E483999-000"},
    {"name": "Straight Jeans", "price": "59.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482279/item/cagoods_69_482279_3x4.jpg?width=200", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482279-000"},
    {"name": "Denim Shorts", "price": "49.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483512/item/cagoods_69_483512_3x4.jpg?width=200", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E483512-000"},
    {"name": "EZY Wide Straight Jeans", "price": "59.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482281/item/cagoods_69_482281_3x4.jpg?width=200", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482281-000"},
    {"name": "Barrel Jeans", "price": "59.90", "color": "Black", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/479000/item/cagoods_00_479000_3x4.jpg?width=200", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E479000-000"},
    {"name": "Cotton Relaxed Ankle Pants", "price": "39.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482243/item/cagoods_54_482243_3x4.jpg?width=200", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482243-000"},
    {"name": "Smart Ankle Pants", "price": "59.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/479298/item/cagoods_09_479298_3x4.jpg?width=200", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E479298-000"},
    {"name": "AIRism Cotton Bra Camisole Dress", "price": "49.90", "color": "Pink", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482808/item/cagoods_16_482808_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482808-000"},
    {"name": "Ribbed Bra Dress Sleeveless", "price": "59.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482802/item/cagoods_05_482802_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482802-000"},
    {"name": "Shift Mini Dress Sleeveless", "price": "29.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483820/item/cagoods_01_483820_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E483820-000"},
    {"name": "Linen Blend Mini Dress Sleeveless", "price": "59.90", "color": "Brown", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482795/item/cagoods_17_482795_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482795-000"},
    {"name": "Linen Blend Tiered Dress", "price": "69.90", "color": "Beige", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482788/item/cagoods_15_482788_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482788-000"},
    {"name": "Linen Blend V Neck Dress", "price": "69.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483823/item/cagoods_09_483823_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E483823-000"},
    {"name": "Denim Mini Skirt", "price": "49.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/485264/item/cagoods_64_485264_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E485264-000"},
    {"name": "Tiered Maxi Skirt", "price": "59.90", "color": "Black", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482286/item/cagoods_00_482286_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482286-000"},
    {"name": "Linen Blend Tuck Long Skirt", "price": "59.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482285/item/cagoods_69_482285_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482285-000"},
    {"name": "Mermaid Maxi Skirt", "price": "29.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484853/item/cagoods_09_484853_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E484853-000"},
    {"name": "Cotton Blend Short Blouson", "price": "79.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/484032/item/cagoods_72_484032_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E484032-000"},
    {"name": "Utility Short Coat", "price": "99.90", "color": "Beige", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483037/item/cagoods_58_483037_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E483037-000"},
    {"name": "Zip-Up Short Jacket", "price": "79.90", "color": "Beige", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/479208/item/cagoods_32_479208_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E479208-000"},
    {"name": "Utility Short Jacket", "price": "89.90", "color": "Green", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/483807/item/cagoods_33_483807_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E483807-000"},
    {"name": "Soft Brushed Short Jacket", "price": "89.90", "color": "Brown", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/485706/item/cagoods_37_485706_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E485706-000"},
    {"name": "Pufftech Collarless Jacket", "price": "39.90", "color": "Blue", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/482274/item/cagoods_69_482274_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E482274-000"},
    {"name": "Double Breasted Jacket", "price": "99.90", "color": "Beige", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/478557/item/cagoods_05_478557_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E478557-000"},
    {"name": "Pufftech Parka", "price": "99.90", "color": "White", "image_url": "https://image.uniqlo.com/UQ/ST3/ca/imagesgoods/469871/item/cagoods_09_469871_3x4.jpg?width=300", "affiliate_url": "https://www.uniqlo.com/ca/en/products/E469871-000"},
]

# ── Brand mapping ──
BRAND_DATA = {
    "GARAGE": GARAGE_RAW,
    "DYNAMITE": DYNAMITE_RAW,
    "LULULEMON": LULULEMON_RAW,
    "ARITZIA": ARITZIA_RAW,
    "ZARA": ZARA_RAW,
    "UNIQLO": UNIQLO_RAW,
}


def upload_to_supabase(products: list[dict]) -> int:
    """Upload normalized products to Supabase, skipping duplicates by image_url."""
    from supabase import create_client

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Fetch existing image URLs
    existing = set()
    page = 0
    while True:
        resp = client.table("products").select("image_url").range(page * 1000, (page + 1) * 1000 - 1).execute()
        if not resp.data:
            break
        existing.update(row["image_url"] for row in resp.data)
        page += 1

    print(f"\nExisting products in DB: {len(existing)}")

    new_products = [p for p in products if p["image_url"] not in existing]
    print(f"New products to upload: {len(new_products)}")

    if not new_products:
        return 0

    batch_size = 50
    uploaded = 0
    for i in range(0, len(new_products), batch_size):
        batch = new_products[i : i + batch_size]
        try:
            client.table("products").insert(batch).execute()
            uploaded += len(batch)
            print(f"  Uploaded {uploaded}/{len(new_products)}")
        except Exception as e:
            print(f"  Batch insert error: {e}")

    return uploaded


def main():
    parser = argparse.ArgumentParser(description="Upload Firecrawl-scraped products")
    parser.add_argument("--dry-run", action="store_true", help="Preview without uploading")
    parser.add_argument("--output", type=str, help="Export to JSON instead of uploading")
    args = parser.parse_args()

    all_products = []
    seen_images = set()

    for brand, raw_list in BRAND_DATA.items():
        normalized = []
        for raw in raw_list:
            product = normalize_product(raw, brand)
            if product and product["image_url"] not in seen_images:
                seen_images.add(product["image_url"])
                normalized.append(product)

        print(f"  {brand}: {len(raw_list)} raw -> {len(normalized)} normalized")
        all_products.extend(normalized)

    print(f"\n{'='*50}")
    print(f"Total normalized products: {len(all_products)}")

    cats = Counter(p["category"] for p in all_products)
    print("\nCategory distribution:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat:12s}: {count}")

    brands = Counter(p["brand"] for p in all_products)
    print("\nBrand distribution:")
    for brand, count in sorted(brands.items(), key=lambda x: -x[1]):
        print(f"  {brand:12s}: {count}")

    if args.dry_run:
        print("\n[DRY RUN] First 5 products:")
        for p in all_products[:5]:
            print(f"  {json.dumps(p, indent=2)}")
        return

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"\nExported to {args.output}")
        return

    uploaded = upload_to_supabase(all_products)
    print(f"\nDone! Uploaded {uploaded} new products.")


if __name__ == "__main__":
    main()
