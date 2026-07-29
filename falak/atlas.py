# -*- coding: utf-8 -*-
"""
الأطلس الفلكي — إحداثيات المدن ومناطقها الزمنية، بلا إنترنت.
الصيغة: عربي|إنجليزي|البلد|خط العرض|خط الطول|المنطقة الزمنية
يمكن دائمًا إدخال الإحداثيات يدويًا إن لم تكن المدينة هنا.
"""
from __future__ import annotations

import unicodedata

_RAW = """
دمشق|Damascus|سوريا|33.5138|36.2765|Asia/Damascus
حلب|Aleppo|سوريا|36.2021|37.1343|Asia/Damascus
حمص|Homs|سوريا|34.7324|36.7137|Asia/Damascus
حماة|Hama|سوريا|35.1318|36.7578|Asia/Damascus
اللاذقية|Latakia|سوريا|35.5196|35.7915|Asia/Damascus
طرطوس|Tartus|سوريا|34.8890|35.8866|Asia/Damascus
دير الزور|Deir ez-Zor|سوريا|35.3359|40.1408|Asia/Damascus
الحسكة|Al-Hasakah|سوريا|36.5024|40.7477|Asia/Damascus
الرقة|Raqqa|سوريا|35.9594|39.0079|Asia/Damascus
إدلب|Idlib|سوريا|35.9306|36.6339|Asia/Damascus
السويداء|As-Suwayda|سوريا|32.7094|36.5694|Asia/Damascus
درعا|Daraa|سوريا|32.6189|36.1021|Asia/Damascus
القنيطرة|Quneitra|سوريا|33.1256|35.8239|Asia/Damascus
بيروت|Beirut|لبنان|33.8938|35.5018|Asia/Beirut
طرابلس|Tripoli|لبنان|34.4367|35.8497|Asia/Beirut
صيدا|Sidon|لبنان|33.5571|35.3729|Asia/Beirut
صور|Tyre|لبنان|33.2705|35.2038|Asia/Beirut
زحلة|Zahle|لبنان|33.8463|35.9019|Asia/Beirut
بعلبك|Baalbek|لبنان|34.0058|36.2181|Asia/Beirut
جونية|Jounieh|لبنان|33.9808|35.6178|Asia/Beirut
عمّان|Amman|الأردن|31.9539|35.9106|Asia/Amman
إربد|Irbid|الأردن|32.5556|35.8500|Asia/Amman
الزرقاء|Zarqa|الأردن|32.0728|36.0880|Asia/Amman
العقبة|Aqaba|الأردن|29.5321|35.0063|Asia/Amman
السلط|Salt|الأردن|32.0392|35.7272|Asia/Amman
القدس|Jerusalem|فلسطين|31.7683|35.2137|Asia/Hebron
غزة|Gaza|فلسطين|31.5017|34.4668|Asia/Hebron
رام الله|Ramallah|فلسطين|31.9038|35.2034|Asia/Hebron
نابلس|Nablus|فلسطين|32.2211|35.2544|Asia/Hebron
الخليل|Hebron|فلسطين|31.5326|35.0998|Asia/Hebron
بيت لحم|Bethlehem|فلسطين|31.7054|35.2024|Asia/Hebron
جنين|Jenin|فلسطين|32.4597|35.3000|Asia/Hebron
حيفا|Haifa|فلسطين|32.7940|34.9896|Asia/Jerusalem
يافا|Jaffa|فلسطين|32.0553|34.7500|Asia/Jerusalem
الناصرة|Nazareth|فلسطين|32.6996|35.3035|Asia/Jerusalem
بغداد|Baghdad|العراق|33.3152|44.3661|Asia/Baghdad
البصرة|Basra|العراق|30.5085|47.7804|Asia/Baghdad
الموصل|Mosul|العراق|36.3350|43.1189|Asia/Baghdad
أربيل|Erbil|العراق|36.1911|44.0092|Asia/Baghdad
النجف|Najaf|العراق|32.0000|44.3300|Asia/Baghdad
كربلاء|Karbala|العراق|32.6160|44.0249|Asia/Baghdad
السليمانية|Sulaymaniyah|العراق|35.5556|45.4351|Asia/Baghdad
كركوك|Kirkuk|العراق|35.4681|44.3922|Asia/Baghdad
الرمادي|Ramadi|العراق|33.4258|43.3089|Asia/Baghdad
الناصرية|Nasiriyah|العراق|31.0439|46.2575|Asia/Baghdad
القاهرة|Cairo|مصر|30.0444|31.2357|Africa/Cairo
الإسكندرية|Alexandria|مصر|31.2001|29.9187|Africa/Cairo
الجيزة|Giza|مصر|30.0131|31.2089|Africa/Cairo
بورسعيد|Port Said|مصر|31.2653|32.3019|Africa/Cairo
السويس|Suez|مصر|29.9668|32.5498|Africa/Cairo
الأقصر|Luxor|مصر|25.6872|32.6396|Africa/Cairo
أسوان|Aswan|مصر|24.0889|32.8998|Africa/Cairo
المنصورة|Mansoura|مصر|31.0409|31.3785|Africa/Cairo
طنطا|Tanta|مصر|30.7865|31.0004|Africa/Cairo
أسيوط|Asyut|مصر|27.1809|31.1837|Africa/Cairo
المنيا|Minya|مصر|28.1099|30.7503|Africa/Cairo
الزقازيق|Zagazig|مصر|30.5877|31.5020|Africa/Cairo
دمنهور|Damanhur|مصر|31.0341|30.4682|Africa/Cairo
الإسماعيلية|Ismailia|مصر|30.5965|32.2715|Africa/Cairo
شرم الشيخ|Sharm El Sheikh|مصر|27.9158|34.3300|Africa/Cairo
الرياض|Riyadh|السعودية|24.7136|46.6753|Asia/Riyadh
جدة|Jeddah|السعودية|21.4858|39.1925|Asia/Riyadh
مكة المكرمة|Mecca|السعودية|21.3891|39.8579|Asia/Riyadh
المدينة المنورة|Medina|السعودية|24.5247|39.5692|Asia/Riyadh
الدمام|Dammam|السعودية|26.4207|50.0888|Asia/Riyadh
الخبر|Khobar|السعودية|26.2794|50.2083|Asia/Riyadh
الطائف|Taif|السعودية|21.2703|40.4158|Asia/Riyadh
تبوك|Tabuk|السعودية|28.3835|36.5662|Asia/Riyadh
أبها|Abha|السعودية|18.2164|42.5053|Asia/Riyadh
بريدة|Buraydah|السعودية|26.3260|43.9750|Asia/Riyadh
حائل|Hail|السعودية|27.5114|41.7208|Asia/Riyadh
الأحساء|Al-Ahsa|السعودية|25.3833|49.5833|Asia/Riyadh
جازان|Jazan|السعودية|16.8892|42.5511|Asia/Riyadh
نجران|Najran|السعودية|17.4924|44.1277|Asia/Riyadh
ينبع|Yanbu|السعودية|24.0895|38.0618|Asia/Riyadh
دبي|Dubai|الإمارات|25.2048|55.2708|Asia/Dubai
أبو ظبي|Abu Dhabi|الإمارات|24.4539|54.3773|Asia/Dubai
الشارقة|Sharjah|الإمارات|25.3463|55.4209|Asia/Dubai
العين|Al Ain|الإمارات|24.2075|55.7447|Asia/Dubai
عجمان|Ajman|الإمارات|25.4052|55.5136|Asia/Dubai
رأس الخيمة|Ras Al Khaimah|الإمارات|25.7895|55.9432|Asia/Dubai
الفجيرة|Fujairah|الإمارات|25.1288|56.3265|Asia/Dubai
الكويت|Kuwait City|الكويت|29.3759|47.9774|Asia/Kuwait
الأحمدي|Ahmadi|الكويت|29.0769|48.0838|Asia/Kuwait
الدوحة|Doha|قطر|25.2854|51.5310|Asia/Qatar
الريان|Al Rayyan|قطر|25.2919|51.4244|Asia/Qatar
المنامة|Manama|البحرين|26.2285|50.5860|Asia/Bahrain
المحرق|Muharraq|البحرين|26.2572|50.6119|Asia/Bahrain
مسقط|Muscat|عُمان|23.5880|58.3829|Asia/Muscat
صلالة|Salalah|عُمان|17.0151|54.0924|Asia/Muscat
صحار|Sohar|عُمان|24.3474|56.7089|Asia/Muscat
نزوى|Nizwa|عُمان|22.9333|57.5333|Asia/Muscat
صنعاء|Sanaa|اليمن|15.3694|44.1910|Asia/Aden
عدن|Aden|اليمن|12.7855|45.0187|Asia/Aden
تعز|Taiz|اليمن|13.5789|44.0219|Asia/Aden
الحديدة|Hodeidah|اليمن|14.7978|42.9545|Asia/Aden
المكلا|Mukalla|اليمن|14.5424|49.1242|Asia/Aden
إب|Ibb|اليمن|13.9667|44.1667|Asia/Aden
الخرطوم|Khartoum|السودان|15.5007|32.5599|Africa/Khartoum
أم درمان|Omdurman|السودان|15.6445|32.4777|Africa/Khartoum
بورتسودان|Port Sudan|السودان|19.6158|37.2164|Africa/Khartoum
نيالا|Nyala|السودان|12.0500|24.8833|Africa/Khartoum
طرابلس الغرب|Tripoli|ليبيا|32.8872|13.1913|Africa/Tripoli
بنغازي|Benghazi|ليبيا|32.1194|20.0868|Africa/Tripoli
مصراتة|Misrata|ليبيا|32.3754|15.0925|Africa/Tripoli
سبها|Sabha|ليبيا|27.0377|14.4283|Africa/Tripoli
تونس|Tunis|تونس|36.8065|10.1815|Africa/Tunis
صفاقس|Sfax|تونس|34.7406|10.7603|Africa/Tunis
سوسة|Sousse|تونس|35.8256|10.6412|Africa/Tunis
القيروان|Kairouan|تونس|35.6781|10.0963|Africa/Tunis
بنزرت|Bizerte|تونس|37.2744|9.8739|Africa/Tunis
قابس|Gabes|تونس|33.8815|10.0982|Africa/Tunis
الجزائر|Algiers|الجزائر|36.7538|3.0588|Africa/Algiers
وهران|Oran|الجزائر|35.6971|-0.6308|Africa/Algiers
قسنطينة|Constantine|الجزائر|36.3650|6.6147|Africa/Algiers
عنابة|Annaba|الجزائر|36.9000|7.7667|Africa/Algiers
باتنة|Batna|الجزائر|35.5559|6.1741|Africa/Algiers
سطيف|Setif|الجزائر|36.1911|5.4137|Africa/Algiers
تلمسان|Tlemcen|الجزائر|34.8828|-1.3167|Africa/Algiers
بسكرة|Biskra|الجزائر|34.8500|5.7333|Africa/Algiers
الدار البيضاء|Casablanca|المغرب|33.5731|-7.5898|Africa/Casablanca
الرباط|Rabat|المغرب|34.0209|-6.8416|Africa/Casablanca
مراكش|Marrakesh|المغرب|31.6295|-7.9811|Africa/Casablanca
فاس|Fez|المغرب|34.0181|-5.0078|Africa/Casablanca
طنجة|Tangier|المغرب|35.7595|-5.8340|Africa/Casablanca
أغادير|Agadir|المغرب|30.4278|-9.5981|Africa/Casablanca
مكناس|Meknes|المغرب|33.8935|-5.5473|Africa/Casablanca
وجدة|Oujda|المغرب|34.6867|-1.9114|Africa/Casablanca
تطوان|Tetouan|المغرب|35.5785|-5.3684|Africa/Casablanca
نواكشوط|Nouakchott|موريتانيا|18.0735|-15.9582|Africa/Nouakchott
مقديشو|Mogadishu|الصومال|2.0469|45.3182|Africa/Mogadishu
جيبوتي|Djibouti|جيبوتي|11.5721|43.1456|Africa/Djibouti
موروني|Moroni|جزر القمر|-11.7172|43.2473|Indian/Comoro
باريس|Paris|فرنسا|48.8566|2.3522|Europe/Paris
مرسيليا|Marseille|فرنسا|43.2965|5.3698|Europe/Paris
ليون|Lyon|فرنسا|45.7640|4.8357|Europe/Paris
تولوز|Toulouse|فرنسا|43.6047|1.4442|Europe/Paris
نيس|Nice|فرنسا|43.7102|7.2620|Europe/Paris
نانت|Nantes|فرنسا|47.2184|-1.5536|Europe/Paris
مونبلييه|Montpellier|فرنسا|43.6108|3.8767|Europe/Paris
ستراسبورغ|Strasbourg|فرنسا|48.5734|7.7521|Europe/Paris
بوردو|Bordeaux|فرنسا|44.8378|-0.5792|Europe/Paris
ليل|Lille|فرنسا|50.6292|3.0573|Europe/Paris
رين|Rennes|فرنسا|48.1173|-1.6778|Europe/Paris
غرونوبل|Grenoble|فرنسا|45.1885|5.7245|Europe/Paris
لندن|London|بريطانيا|51.5074|-0.1278|Europe/London
مانشستر|Manchester|بريطانيا|53.4808|-2.2426|Europe/London
برمنغهام|Birmingham|بريطانيا|52.4862|-1.8904|Europe/London
غلاسكو|Glasgow|بريطانيا|55.8642|-4.2518|Europe/London
ليفربول|Liverpool|بريطانيا|53.4084|-2.9916|Europe/London
إدنبرة|Edinburgh|بريطانيا|55.9533|-3.1883|Europe/London
برلين|Berlin|ألمانيا|52.5200|13.4050|Europe/Berlin
ميونخ|Munich|ألمانيا|48.1351|11.5820|Europe/Berlin
هامبورغ|Hamburg|ألمانيا|53.5511|9.9937|Europe/Berlin
فرانكفورت|Frankfurt|ألمانيا|50.1109|8.6821|Europe/Berlin
كولونيا|Cologne|ألمانيا|50.9375|6.9603|Europe/Berlin
شتوتغارت|Stuttgart|ألمانيا|48.7758|9.1829|Europe/Berlin
دوسلدورف|Dusseldorf|ألمانيا|51.2277|6.7735|Europe/Berlin
مدريد|Madrid|إسبانيا|40.4168|-3.7038|Europe/Madrid
برشلونة|Barcelona|إسبانيا|41.3874|2.1686|Europe/Madrid
إشبيلية|Seville|إسبانيا|37.3891|-5.9845|Europe/Madrid
فالنسيا|Valencia|إسبانيا|39.4699|-0.3763|Europe/Madrid
غرناطة|Granada|إسبانيا|37.1773|-3.5986|Europe/Madrid
قرطبة|Cordoba|إسبانيا|37.8882|-4.7794|Europe/Madrid
روما|Rome|إيطاليا|41.9028|12.4964|Europe/Rome
ميلانو|Milan|إيطاليا|45.4642|9.1900|Europe/Rome
نابولي|Naples|إيطاليا|40.8518|14.2681|Europe/Rome
تورينو|Turin|إيطاليا|45.0703|7.6869|Europe/Rome
فلورنسا|Florence|إيطاليا|43.7696|11.2558|Europe/Rome
البندقية|Venice|إيطاليا|45.4408|12.3155|Europe/Rome
أمستردام|Amsterdam|هولندا|52.3676|4.9041|Europe/Amsterdam
روتردام|Rotterdam|هولندا|51.9244|4.4777|Europe/Amsterdam
بروكسل|Brussels|بلجيكا|50.8503|4.3517|Europe/Brussels
أنتويرب|Antwerp|بلجيكا|51.2194|4.4025|Europe/Brussels
زيورخ|Zurich|سويسرا|47.3769|8.5417|Europe/Zurich
جنيف|Geneva|سويسرا|46.2044|6.1432|Europe/Zurich
برن|Bern|سويسرا|46.9480|7.4474|Europe/Zurich
فيينا|Vienna|النمسا|48.2082|16.3738|Europe/Vienna
ستوكهولم|Stockholm|السويد|59.3293|18.0686|Europe/Stockholm
غوتنبرغ|Gothenburg|السويد|57.7089|11.9746|Europe/Stockholm
مالمو|Malmo|السويد|55.6050|13.0038|Europe/Stockholm
أوسلو|Oslo|النرويج|59.9139|10.7522|Europe/Oslo
كوبنهاغن|Copenhagen|الدنمارك|55.6761|12.5683|Europe/Copenhagen
هلسنكي|Helsinki|فنلندا|60.1699|24.9384|Europe/Helsinki
لشبونة|Lisbon|البرتغال|38.7223|-9.1393|Europe/Lisbon
بورتو|Porto|البرتغال|41.1579|-8.6291|Europe/Lisbon
أثينا|Athens|اليونان|37.9838|23.7275|Europe/Athens
سالونيك|Thessaloniki|اليونان|40.6401|22.9444|Europe/Athens
وارسو|Warsaw|بولندا|52.2297|21.0122|Europe/Warsaw
كراكوف|Krakow|بولندا|50.0647|19.9450|Europe/Warsaw
براغ|Prague|التشيك|50.0755|14.4378|Europe/Prague
بودابست|Budapest|المجر|47.4979|19.0402|Europe/Budapest
بوخارست|Bucharest|رومانيا|44.4268|26.1025|Europe/Bucharest
صوفيا|Sofia|بلغاريا|42.6977|23.3219|Europe/Sofia
بلغراد|Belgrade|صربيا|44.7866|20.4489|Europe/Belgrade
زغرب|Zagreb|كرواتيا|45.8150|15.9819|Europe/Zagreb
سراييفو|Sarajevo|البوسنة|43.8563|18.4131|Europe/Sarajevo
موسكو|Moscow|روسيا|55.7558|37.6173|Europe/Moscow
سان بطرسبرغ|Saint Petersburg|روسيا|59.9311|30.3609|Europe/Moscow
كييف|Kyiv|أوكرانيا|50.4501|30.5234|Europe/Kyiv
إسطنبول|Istanbul|تركيا|41.0082|28.9784|Europe/Istanbul
أنقرة|Ankara|تركيا|39.9334|32.8597|Europe/Istanbul
إزمير|Izmir|تركيا|38.4237|27.1428|Europe/Istanbul
أنطاليا|Antalya|تركيا|36.8969|30.7133|Europe/Istanbul
بورصة|Bursa|تركيا|40.1826|29.0665|Europe/Istanbul
أضنة|Adana|تركيا|37.0000|35.3213|Europe/Istanbul
غازي عنتاب|Gaziantep|تركيا|37.0662|37.3833|Europe/Istanbul
قونية|Konya|تركيا|37.8746|32.4932|Europe/Istanbul
طهران|Tehran|إيران|35.6892|51.3890|Asia/Tehran
مشهد|Mashhad|إيران|36.2605|59.6168|Asia/Tehran
أصفهان|Isfahan|إيران|32.6539|51.6660|Asia/Tehran
شيراز|Shiraz|إيران|29.5918|52.5837|Asia/Tehran
تبريز|Tabriz|إيران|38.0800|46.2919|Asia/Tehran
قم|Qom|إيران|34.6416|50.8746|Asia/Tehran
الأهواز|Ahvaz|إيران|31.3183|48.6706|Asia/Tehran
كابول|Kabul|أفغانستان|34.5553|69.2075|Asia/Kabul
إسلام آباد|Islamabad|باكستان|33.6844|73.0479|Asia/Karachi
كراتشي|Karachi|باكستان|24.8607|67.0011|Asia/Karachi
لاهور|Lahore|باكستان|31.5204|74.3587|Asia/Karachi
نيودلهي|New Delhi|الهند|28.6139|77.2090|Asia/Kolkata
مومباي|Mumbai|الهند|19.0760|72.8777|Asia/Kolkata
بنغالور|Bangalore|الهند|12.9716|77.5946|Asia/Kolkata
كولكاتا|Kolkata|الهند|22.5726|88.3639|Asia/Kolkata
حيدر آباد|Hyderabad|الهند|17.3850|78.4867|Asia/Kolkata
تشيناي|Chennai|الهند|13.0827|80.2707|Asia/Kolkata
دكا|Dhaka|بنغلاديش|23.8103|90.4125|Asia/Dhaka
كولومبو|Colombo|سريلانكا|6.9271|79.8612|Asia/Colombo
كاتماندو|Kathmandu|نيبال|27.7172|85.3240|Asia/Kathmandu
بكين|Beijing|الصين|39.9042|116.4074|Asia/Shanghai
شنغهاي|Shanghai|الصين|31.2304|121.4737|Asia/Shanghai
غوانزو|Guangzhou|الصين|23.1291|113.2644|Asia/Shanghai
شنتشن|Shenzhen|الصين|22.5431|114.0579|Asia/Shanghai
هونغ كونغ|Hong Kong|الصين|22.3193|114.1694|Asia/Hong_Kong
طوكيو|Tokyo|اليابان|35.6762|139.6503|Asia/Tokyo
أوساكا|Osaka|اليابان|34.6937|135.5023|Asia/Tokyo
كيوتو|Kyoto|اليابان|35.0116|135.7681|Asia/Tokyo
سيول|Seoul|كوريا الجنوبية|37.5665|126.9780|Asia/Seoul
سنغافورة|Singapore|سنغافورة|1.3521|103.8198|Asia/Singapore
كوالالمبور|Kuala Lumpur|ماليزيا|3.1390|101.6869|Asia/Kuala_Lumpur
جاكرتا|Jakarta|إندونيسيا|-6.2088|106.8456|Asia/Jakarta
بانكوك|Bangkok|تايلاند|13.7563|100.5018|Asia/Bangkok
مانيلا|Manila|الفلبين|14.5995|120.9842|Asia/Manila
هانوي|Hanoi|فيتنام|21.0285|105.8542|Asia/Ho_Chi_Minh
باكو|Baku|أذربيجان|40.4093|49.8671|Asia/Baku
تبليسي|Tbilisi|جورجيا|41.7151|44.8271|Asia/Tbilisi
يريفان|Yerevan|أرمينيا|40.1792|44.4991|Asia/Yerevan
طشقند|Tashkent|أوزبكستان|41.2995|69.2401|Asia/Tashkent
ألماتي|Almaty|كازاخستان|43.2220|76.8512|Asia/Almaty
نيويورك|New York|أمريكا|40.7128|-74.0060|America/New_York
لوس أنجلوس|Los Angeles|أمريكا|34.0522|-118.2437|America/Los_Angeles
شيكاغو|Chicago|أمريكا|41.8781|-87.6298|America/Chicago
هيوستن|Houston|أمريكا|29.7604|-95.3698|America/Chicago
واشنطن|Washington DC|أمريكا|38.9072|-77.0369|America/New_York
سان فرانسيسكو|San Francisco|أمريكا|37.7749|-122.4194|America/Los_Angeles
ميامي|Miami|أمريكا|25.7617|-80.1918|America/New_York
بوسطن|Boston|أمريكا|42.3601|-71.0589|America/New_York
سياتل|Seattle|أمريكا|47.6062|-122.3321|America/Los_Angeles
ديترويت|Detroit|أمريكا|42.3314|-83.0458|America/Detroit
فيلادلفيا|Philadelphia|أمريكا|39.9526|-75.1652|America/New_York
أطلانطا|Atlanta|أمريكا|33.7490|-84.3880|America/New_York
دالاس|Dallas|أمريكا|32.7767|-96.7970|America/Chicago
فينيكس|Phoenix|أمريكا|33.4484|-112.0740|America/Phoenix
دنفر|Denver|أمريكا|39.7392|-104.9903|America/Denver
لاس فيغاس|Las Vegas|أمريكا|36.1699|-115.1398|America/Los_Angeles
تورونتو|Toronto|كندا|43.6532|-79.3832|America/Toronto
مونتريال|Montreal|كندا|45.5017|-73.5673|America/Toronto
فانكوفر|Vancouver|كندا|49.2827|-123.1207|America/Vancouver
أوتاوا|Ottawa|كندا|45.4215|-75.6972|America/Toronto
كالغاري|Calgary|كندا|51.0447|-114.0719|America/Edmonton
مكسيكو سيتي|Mexico City|المكسيك|19.4326|-99.1332|America/Mexico_City
هافانا|Havana|كوبا|23.1136|-82.3666|America/Havana
ساو باولو|Sao Paulo|البرازيل|-23.5505|-46.6333|America/Sao_Paulo
ريو دي جانيرو|Rio de Janeiro|البرازيل|-22.9068|-43.1729|America/Sao_Paulo
بوينس آيرس|Buenos Aires|الأرجنتين|-34.6037|-58.3816|America/Argentina/Buenos_Aires
سانتياغو|Santiago|تشيلي|-33.4489|-70.6693|America/Santiago
ليما|Lima|بيرو|-12.0464|-77.0428|America/Lima
بوغوتا|Bogota|كولومبيا|4.7110|-74.0721|America/Bogota
كاراكاس|Caracas|فنزويلا|10.4806|-66.9036|America/Caracas
لاغوس|Lagos|نيجيريا|6.5244|3.3792|Africa/Lagos
أبوجا|Abuja|نيجيريا|9.0765|7.3986|Africa/Lagos
أكرا|Accra|غانا|5.6037|-0.1870|Africa/Accra
داكار|Dakar|السنغال|14.7167|-17.4677|Africa/Dakar
أبيدجان|Abidjan|ساحل العاج|5.3600|-4.0083|Africa/Abidjan
أديس أبابا|Addis Ababa|إثيوبيا|9.0320|38.7469|Africa/Addis_Ababa
نيروبي|Nairobi|كينيا|-1.2864|36.8172|Africa/Nairobi
دار السلام|Dar es Salaam|تنزانيا|-6.7924|39.2083|Africa/Dar_es_Salaam
كمبالا|Kampala|أوغندا|0.3476|32.5825|Africa/Kampala
جوهانسبرغ|Johannesburg|جنوب أفريقيا|-26.2041|28.0473|Africa/Johannesburg
كيب تاون|Cape Town|جنوب أفريقيا|-33.9249|18.4241|Africa/Johannesburg
سيدني|Sydney|أستراليا|-33.8688|151.2093|Australia/Sydney
ملبورن|Melbourne|أستراليا|-37.8136|144.9631|Australia/Melbourne
بريزبن|Brisbane|أستراليا|-27.4698|153.0251|Australia/Brisbane
بيرث|Perth|أستراليا|-31.9505|115.8605|Australia/Perth
أوكلاند|Auckland|نيوزيلندا|-36.8485|174.7633|Pacific/Auckland
"""


def _norm(s: str) -> str:
    """تطبيع للبحث: إزالة التشكيل وتوحيد الألف والهاء والياء."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    for a, b in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"),
                 ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي"), ("ـ", "")):
        s = s.replace(a, b)
    return s.lower().strip()


def _load():
    out = []
    for line in _RAW.strip().splitlines():
        p = line.split("|")
        if len(p) != 6:
            continue
        ar, en, country, lat, lon, tz = p
        out.append({
            "ar": ar, "en": en, "country": country,
            "lat": float(lat), "lon": float(lon), "tz": tz,
            "label": f"{ar} — {country}",
            "_k": _norm(ar) + " " + _norm(en) + " " + _norm(country),
        })
    return out


CITIES = _load()


def search_local(q: str, limit: int = 12):
    """بحث في الأطلس المحلّي — فوري وبلا إنترنت."""
    q = _norm(q)
    if not q:
        return []
    starts, contains = [], []
    for c in CITIES:
        if _norm(c["ar"]).startswith(q) or _norm(c["en"]).startswith(q):
            starts.append(c)
        elif q in c["_k"]:
            contains.append(c)
    res = (starts + contains)[:limit]
    return [dict({k: v for k, v in c.items() if not k.startswith("_")},
                 source="محلّي") for c in res]


# ── الاحتياط العالمي: Open-Meteo Geocoding ──────────────────────
# مجانية بلا مفتاح ولا تسجيل، وتُرجع الإحداثيات والمنطقة الزمنية.
_REMOTE_URL = "https://geocoding-api.open-meteo.com/v1/search"
_REMOTE_CACHE: dict = {}


def search_remote(q: str, limit: int = 8, timeout: float = 4.0):
    """أي قرية في العالم لا يعرفها الأطلس المحلّي."""
    import json
    import urllib.parse
    import urllib.request

    q = (q or "").strip()
    if len(q) < 2:
        return []
    ck = (q, limit)
    if ck in _REMOTE_CACHE:
        return _REMOTE_CACHE[ck]

    out = []
    for lang in ("ar", "en"):
        url = _REMOTE_URL + "?" + urllib.parse.urlencode(
            {"name": q, "count": limit, "language": lang, "format": "json"})
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8"))
        except Exception:
            continue
        for h in (data.get("results") or []):
            if not h.get("timezone"):
                continue
            name = h.get("name", "")
            country = h.get("country", "")
            admin = h.get("admin1") or ""
            out.append({
                "ar": name, "en": name, "country": country,
                "lat": round(float(h["latitude"]), 4),
                "lon": round(float(h["longitude"]), 4),
                "tz": h["timezone"],
                "label": " — ".join(x for x in (name, admin, country) if x),
                "source": "عالمي",
            })
        if out:
            break

    # إزالة التكرار بحسب الموضع
    seen, uniq = set(), []
    for c in out:
        k = (round(c["lat"], 2), round(c["lon"], 2))
        if k not in seen:
            seen.add(k)
            uniq.append(c)
    uniq = uniq[:limit]
    _REMOTE_CACHE[ck] = uniq
    return uniq


def search(q: str, limit: int = 12, remote: bool = True):
    """
    الأطلس المحلّي أولًا (فوري، بأسماء عربية مضبوطة)،
    ثم الاحتياط العالمي لِما لم يوجد فيه.
    """
    local = search_local(q, limit)
    if len(local) >= 3 or not remote:
        return local
    extra = search_remote(q, limit - len(local))
    have = {(round(c["lat"], 1), round(c["lon"], 1)) for c in local}
    for c in extra:
        if (round(c["lat"], 1), round(c["lon"], 1)) not in have:
            local.append(c)
    return local[:limit]


def find(name: str, remote: bool = True):
    """أفضل تطابق لاسم مدينة، أو None."""
    r = search_local(name, 1)
    if r:
        return r[0]
    if remote:
        r = search_remote(name, 1)
        if r:
            return r[0]
    return None
