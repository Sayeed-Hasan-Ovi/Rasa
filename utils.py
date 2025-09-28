import re
from langdetect import detect
import datetime

static_bangla_messages = {
    "new_meter_document": "নতুন সংযোগ এর প্রয়োজনীয় ডকুমেন্ট সম্পর্কে জানতে ক্লিক <a href='https://dpdc.org.bd/site/nocs/citizen_charter/-' target='_blank'>এই লিংক এ ক্লিক করুন </a>",
    "new_meter_payment": "নতুন সংযোগ এর ক্ষেত্রে ডিমান্ড ফী সম্পর্কে জানতে ক্লিক <a href='https://dpdc.org.bd/site/nocs/citizen_charter/-' target='_blank'>এই লিংক এ ক্লিক করুন </a>",
    "new_meter_price": "নতুন সংযোগ এর ক্ষেত্রে ডিমান্ড ফী সম্পর্কে জানতে ক্লিক <a href='https://dpdc.org.bd/site/nocs/citizen_charter/-' target='_blank'>এই লিংক এ ক্লিক করুন </a>",
    "new_meter_expected_days": "ডকুমেন্টস সঠিক থাকলে এলটি সংযোগ ৪ দিনে এবং এইচটি সংযোগ ১৫ দিনে প্রদান করা হবে।  বিস্তারিত জানতে আমাদের হেল্প লাইন (১৬১১৬) এ যোগাযোগ করুন ",
    "new_meter_provider": "প্রিপেইড এর ক্ষেত্রে ডিপিডিসি প্রদান করবে এবং পোস্টপেইড এর ক্ষেত্রে গ্রাহককে কিনে দিতে হবে।  বিস্তারিত জানতে আমাদের হেল্প লাইন (১৬১১৬) এ যোগাযোগ করুন ",
    "provide_bill_number": "অনুগ্রহ করে আপনার বিল নম্বরটি লিখুন",
    "invalid_bill_number": "প্রদানকৃত বিল নম্বর দিয়ে কোনো বিল পাওয়া যায় নি। অন্য বিল নম্বর প্রদান করতে চান?",
    "no_electricity_complaint_registered": "আপনার অভিযোগ টি আমরা গ্রহণ করেছি, অল্প সময়ের মধ্যেই আমাদের একজন প্রতিনিধি আপনার সাথে যোগাযোগ করবেন",
    "check_meter_balance": "অনুগ্রহ করে আপনার মিটারের ব্যালান্স পরীক্ষা করে দেখুন মিটারে পর্যাপ্ত ব্যালান্স রয়েছে কি না ?",
    "recharge_for_electricity": "নিরবিচ্ছিন্ন বিদ্যুৎ সেবা পেতে অনুগ্রহ করে আপনার মিটারটি রিচার্জ করুন",
    "not_prepaid_meter": "আপনার মিটার টি প্রিপেইড মিটার নই। অনুগ্রহ করে আমাদের হেল্প লাইন (১৬১১৬) এ যোগাযোগ করুন",
    "provide_sequence": "মিটার এ ৮৮৯ চেপে সিকোয়েন্স কোডটি দেখে তা লিখুন",
    "provide_customer_number": "অনুগ্রহ করে আপনার গ্রাহক নম্বরটি লিখুন",
    "invalid_customer_number": "আপনি যে গ্রাহক নম্বর দিয়েছেন সেটি সঠিক নয়। আপনি বিদ্যুৎ বিলের কপি/রিচার্জ এর কপি/প্রি-পেইড কার্ড থেকে আপনার গ্রাহক নাম্বর জানতে পারবেন<br><br>আপনি কি আবার গ্রাহক নাম্বার লিখতে চান?",
    "provide_phone_number": "অনুগ্রহ করে আপনার মোবাইল নম্বরটি লিখুন",
    "invalid_phone_number": "মোবাইল নম্বরটি সঠিক নয়। অনুগ্রহ করে আমাদের হেল্প লাইন (১৬১১৬) এ যোগাযোগ করুন",
    "did_online_register": "আপনি কি অনলাইন এ আবেদন করেছেন?",
    "provide_tracking_number": "অনুগ্রহ করে আপনার অনলাইন আবেদনের ট্র্যাকিং নম্বরটি লিখুন",
    "bill_payment_issue": "সমস্যাটির জন্য আমরা আন্তরিক ভাবে দুঃখিত। MFS, Internet Banking, Online Banking ইত্যাদি মাধ্যমে পুনরায় চেষ্টা করুন । অন্যথায় আমাদের হেল্প লাইন (১৬১১৬) এ যোগাযোগ করুন",
    "retry_tracking_number": "ট্র্যাকিং নম্বরটি সঠিক নয়। অনুগ্রহ করে আবার সঠিক ট্র্যাকিং নম্বর দিন।",
    "invalid_tracking_number": "ট্র্যাকিং নম্বরটি সঠিক নয়। অনুগ্রহ করে আমাদের হেল্পলাইন (১৬১১৬) এ যোগাযোগ করুন। ",
    "new_registration": "অনলাইন এর মাধ্যমে আবেদনের জন্য <a href='https://onlineapplication.dpdc.org.bd/home.php' target='_blank'>এই লিংক</a> এ ক্লিক করুন",
    "unable_to_reach_dpdc_server": "আমারা আন্তরিকভাবে দুঃখিত, সার্ভারে যোগাযোগ করা যাচ্ছে না। অনুগ্রহ করে কিছুক্ষন পর আবার চেষ্টা করুন অথবা আমাদের হেল্প লাইন (১৬১১৬) এ যোগাযোগ করুনন",
    "not_found": "আমরা আন্তরিকভাবে দুঃখিত আপনার সমস্যাটি অনুধাবন করা যাই নি। আমি কৃত্তিম বুদ্ধিমত্তা সম্পন্ন একটি সার্ভিস যা কেবল চালু করা হয়েছে। আমি এখনো শিখছি এবং একজন ভালো প্রশিক্ষনার্থি। আশা করি খুব শীঘ্রই আপনার সকল সেবা প্রদান করতে সক্ষম হব। ডিপিডিসি’র সাথে থাকার জন্য ধন্যবাদ।",
    "call_center_issue": "আপনার অসুবিধার জন্য দুঃখিত, কিছুক্ষণ পর আবার চেষ্টা করুন",
    "forgot_customer_number": "যদি আপনি আপনার কাস্টমার নাম্বার ভুলে যান  দয়া করে কাস্টমার সাপোর্টে ১৬১৬ নাম্বারে কল করুন।",
    "for_more_query": "ডিপিডিসি স্মার্ট কাস্টমার এসিস্ট্যান্ট- চ্যাটবট ”বিদ্যুৎ বন্ধু” ব্যবহার এর জন্য আপনাকে ধন্যবাদ।<br> যেকোনো সময় যেকোনো তথ্যের জন্য বিদ্যুৎ বন্ধুর সহায়তা নিন অথবা আমাদের হেল্প লাইন (১৬১১৬) এ যোগাযোগ করুন",
    "confirm_complaint":"আপনি কি অভিযোগ দাখিল করতে চান?",
    "confirm_complaint_no_electricity":"আমরা আন্তরিকভাবে দুঃখিত, এই মুহূর্তে আপনার এলাকায় কোনো সিডিউল ইন্টারাপ্সন/মেইনটেন্যান্স নাই।<br> উক্ত ব্যাপারে আপনি কি অভিযোগ দাখিল করতে চান?",
    "query_about_customer_number":"প্রিয় গ্রাহক, আপনার গ্রাহক নাম্বারটি জানা আছে কি?",
    "provide_complain_no": "অনুগ্রহ করে আপনার অভিযোগ নম্বরটি লিখুন",

    "demand_charge": "ডিমান্ড চার্জের মাধ্যমে ডিপিডিসি সহ সকল বিতরণ সংস্থা সরকারের নির্দেশে  গ্রাহকের কাছ থেকে বিদ্যুৎ সরবরাহের জন্য প্রয়োজনীয় যন্ত্রপাতি, মালামাল, এবং অবকাঠামো নির্মাণ ও রক্ষণাবেক্ষণের খরচ আদায় করে। সংযুক্ত লোডের বিপরীতে সরকার কর্তৃক নির্ধারিত হারে ডিমান্ড চার্জ আরোপ করা হয়। ",
    "surcharge": "সারচার্জ/LPS/ এলপিএস হল একটি অতিরিক্ত ফি বা চার্জ যা মাসিক বিদ্যুৎ বিল নির্ধারিত সময়ে পরিশোধ না করলে জরিমানার জন্য যোগ করা হয়। বাংলাদেশ এনার্জি রেগুলোটরী কমিশন কর্তৃক এককালীন ৫% হারে এ জরিমানা আরোপ করা হয়। ",
    "call_center_info": "১৬১১৬",
    "vat_query": "সরকার নির্ধারিত হারে ভ্যালু এডেড ট্যাক্স (ভ্যাট) আরোপ করা হয়। বর্তমানে বিদ্যুৎ বিলের জন্য ৫% হারে ভ্যাট ধার্য রয়েছে।",
    "raise_complaint": "আপনার অসুবিধার জন্য দুঃখিত। অভিযোগ দাখিলের জন্য ডিপিডিসি’র কল সেন্টার ‘১৬১১৬’ এ কল করুন",
    "rebate_query": "০.০৫% হারে রিবেট দেয়া হয়",
    "balance_query": "আপনার মিটার অনুযায়ী নির্দেশিকা জানতে <a href='https://dpdc.portal.gov.bd/site/page/9ac7abe8-c922-4cef-bab5-b4f9af08ca0d' target='_blank'>`প্রিপেইড মিটার সংক্রান্ত সেবা`</a> ক্লিক করুন",
    "recharge_commission": "বিটিআরসি কর্তৃক নির্ধারিত হারে ৪০০ টাকা পর্যন্ত রিচার্জে ৫ টাকা, ৪০১ টাকা হতে ১৫০০ টাকা পর্যন্ত ১০ টাকা, ১৫০১ টাকা হতে ৫০০০ টাকা পর্যন্ত ১৫ টাকা এবং ৫০০১ বা তদোর্দ্ধ টাকা রিচার্জের জন্য ২৫ টাকা হারে কমিশন দিতে হয়। ",
    "no_bill": "আপনার অসুবিধার জন্য দুঃখিত। অভিযোগ দাখিলের জন্য ডিপিডিসি’র কল সেন্টার ‘১৬১১৬’ এ কল করুন অথবা আপনার সংশিষ্ট বিদ্যুৎ অফিষে যোগাযোগ করুন ।",
    "non_online_recharge": "আপনার মিটার যদি স্মার্ট বা কী-প্যাড হয় তাহলে বিকাশ বা রকেটের মাধ্যমে রিচার্জ করতে পারবেন। শীঘ্রই ডিপিডিসি’র সকল মিটার অনলাইনে রুপান্তরিত করা হবে।",
    "increase_capacity": "আপনার মিটারের লোড বৃদ্ধি করতে ডিপিডিসির ওয়েবসাইটের <a href='https://dpdc.org.bd/site/nocs/citizen_charter/-' target='_blank'>“সিটিজেন চার্টার”</a> এ ক্লিক করে আবেদন করুন।",
    "fix_name": "আপনার নাম সংশোধন বা পরিবর্তন করতে <a href='https://onlineapplication.dpdc.org.bd/home.php' target='_blank'>এখানে ক্লিক</a> করে আবেদন করুন।",
    "fix_address": "আপনার ঠিকানা সংশোধন বা পরিবর্তন করতে <a href='https://onlineapplication.dpdc.org.bd/home.php' target='_blank'>এখানে ক্লিক</a> করে আবেদন করুন।",
    "dpdc_website": "<a href='https://dpdc.gov.bd' target='_blank'>www.dpdc.gov.bd</a>",
    "dpdc_facebook": "<a href='https://facebook.com/dpdcbd' target='_blank'>www.facebook.com/dpdcbd</a>",
    "pay_online": "অনলাইনে বিল পরিশোধের জন্য ডিপিডিসির ওয়েবসাইটের <a href='https://dpdc.gov.bd/site/page/c3697773-e03c-41ee-b1c8-043d7e7bf1db/-' target='_blank'>এখানে ক্লিক</a> করুন।",
    "want_prepaid_meter": "আপনার এলাকাসহ ডিপিডিসি’র সকল গ্রাহককে খুব শীঘ্রই প্রিপেইড মিটারের আওতায় নিয়ে আসা হবে। আপনার আগ্রহের জন্য ধন্যবাদ।",
    "solar_panel_requirements": "বাংলাদেশ সরকারের নির্দেশনা মোতাবেক আবাসিক গ্রাহকের ক্ষেত্রে অনুমোদিত লোড ১০ কিলোওয়াট বা এর বেশী হলে সোলার প্যানেল স্থাপন করতে হবে। এছাড়া, শিল্প ও বানিজ্যিক সংযোগের ক্ষেত্রে মোট অনুমোদিত লোডের ১০%  সোলার প্যানেল স্থাপন করতে হবে। উভয় ক্ষেত্রে নেট মিটার স্থাপন করে গ্রাহক জাতীয় গ্রীডে বিদ্যুৎ সাশ্রয় করে নিজের বিল কমিয়ে লাভবান হতে পারেন।",
    "net_metering_query": "অনলাইনে নেটমিটারিং এর আবেদনের জন্য বিদ্যুৎ বিভাগের <a href='https://nem.powerdivision.gov.bd/' target='_blank'>ওয়েবসাইট</a> এ ভিজিট করুন।",
    "dpdc_info": "ডিপিডিসি’র কর্মকর্তাদের তথ্য জানতে <a href='https://dpdc.org.bd/site/nocs/all_employee' target='_blank'>এই লিংকে</a> ক্লিক করুন",
    "power_division_complaint_address": "<a href='http://202.51.182.190:5412/ticket' target='_blank'>http://202.51.182.190:5412/ticket</a>",
    "prepaid_meter_rent_query": "প্রিপেইড মিটার ডিপিডিসি কর্তৃক ক্রয় করে স্থাপন করা হচ্ছে বিধায় সরকার কর্তৃক নির্ধারিত হারে মাসিক ভাড়া নেয়া হয়। উল্লেখ্য যে, মিটার নষ্ট হলে ডিপিডিসি কর্তৃক নতুন মিটার স্থাপন করা হয়ে থাকে। আপনার মতামতের জন্য ধন্যবাদ",
    "tariff_rate_query": "ট্যারিফ রেট জানতে <a href='https://dpdc.portal.gov.bd/site/page/27e77af7-1187-436c-9f80-b579d3493a46/-' target='_blank'>এখানে ক্লিক</a> করুন।",
    "chatbot_complaint": "আমি কৃত্তিম বুদ্ধিমত্তা সম্পন্ন একটি সার্ভিস যা কেবল চালু করা হয়েছে। আমি এখনো শিখছি এবং একজন ভালো প্রশিক্ষনার্থি। আশা করি খুব শীঘ্রই আপনার সকল সেবা প্রদান করতে সক্ষম হব। ডিপিডিসি’র সাথে থাকার জন্য ধন্যবাদ। বিস্তারিত জানতে ডিপিডিসি’র কল সেন্টার ‘১৬১১৬’ এ কল করুন।",
    "service_compliment": "আপনার মতামতের জন্য ধন্যবাদ। সব সময় আমাদের পাশে থেকে সহযোগীতা করবেন। বিস্তারিত জানতে ডিপিডিসি’র কল সেন্টার ‘১৬১১৬’ এ কল করুন।",
    "electricity_division_call_center_number": "১৬৯৯৯",
    "desco_call_center_number": "১৬১২০",
    "nocs_address": "আপনার ঠিকানার জন্য <a href='https://dpdc.org.bd/site/nocs/index_gov/-' target='_blank'>”এওসিএস অফিস লিংক”</a> এ ক্লিক করুন",

    "mujibur_rahman_1": "শেখ মুজিবুর রহমান, সংক্ষিপ্তাকারে শেখ মুজিব বা বঙ্গবন্ধু, ছিলেন বাংলাদেশের প্রথম রাষ্ট্রপতি ও দক্ষিণ এশিয়ার অন্যতম প্রভাবশালী রাজনৈতিক ব্যক্তিত্ব। তিনি ভারত বিভাজন আন্দোলনে সক্রিয় অংশগ্রহণ করেন এবং পরবর্তীকালে পূর্ব পাকিস্তানকে স্বাধীন দেশ হিসেবে প্রতিষ্ঠার সংগ্রামে কেন্দ্রীয়ভাবে নেতৃত্ব প্রদান করেন।",
    "sheikh_hasina": "শেখ হাসিনা ওয়াজেদ বাংলাদেশের বর্তমান প্রধানমন্ত্রী। তিনি বাংলাদেশের একাদশ জাতীয় সংসদের সরকারদলীয় প্রধান এবং বাংলাদেশ আওয়ামী লীগের সভানেত্রী। তিনি বাংলাদেশের ইতিহাসে সবচেয়ে দীর্ঘ সময় ধরে দায়িত্ব পালন করা প্রধানমন্ত্রী। তিনি মোট ৮ বার সংসদ সদস্য নির্বাচিত হন",
    "president_of_bangladesh": "মোহাম্মদ সাহাবুদ্দিন হলেন বাংলাদেশের বর্তমান রাষ্ট্রপতি। বাংলাদেশের ২২তম রাষ্ট্রপতি হিসেবে তিনি ২৪ এপ্রিল ২০২৩ তারিখ থেকে দায়িত্বাধীন আছেন। রাষ্ট্রপতি হওয়ার পূর্বে তিনি জেলা ও দায়রা জজ ও দুর্নীতি দমন কমিশনের কমিশনার ছিলেন।",
    "liberation_war": "বাংলাদেশের স্বাধীনতা যুদ্ধ হল ১৯৭১ খ্রিষ্টাব্দে তৎকালীন পশ্চিম পাকিস্তানের বিরুদ্ধে পূর্ব পাকিস্তানে সংঘটিত একটি বিপ্লব ও সশস্ত্র সংগ্রাম। পূর্ব পাকিস্তানে বাঙালি জাতীয়তাবাদের উত্থান ও স্বাধিকার আন্দোলনের ধারাবাহিকতায় এবং বাঙালি গণহত্যার প্রেক্ষিতে এই জনযুদ্ধ সংঘটিত হয়।",
    "about_dpdc": """ঢাকা পাওয়ার ডিস্ট্রিবিউশন কোম্পানি লিমিটেড (ডিপিডিসি) বাংলাদেশের বৃহত্তম বিদ্যুৎ বিতরণ কোম্পানি। ঢাকা পাওয়ার ডিস্ট্রিবিউশন কোম্পানি লিমিটেড (ডিপিডিসি) ২৫ অক্টোবর, ২০০৫ সালে কোম্পানি আইন ১৯৯৪ এর অধীনে গঠিত হয় যার অনুমোদিত শেয়ার ১০,০০০ (দশ হাজার) কোটি যা ১০০ (একশত) কোটি ১০০ টাকা দামের সাধারণ শেয়ারে বিভক্ত।<br>
২৫ অক্টোবর, ২০০৫ থেকে ডিপিডিসি ব্যবসা আরম্ভ করার অনুমতি লাভ করে এবং অপারেশন শুরু করে ১৪ মে ২০০৭ থেকে। ডেসা থেকে সকল সম্পদ ও দায় দায়িত্ব গ্রহণ করে ১লা জুলাই, ২০০৮ থেকে কোম্পানি বাণিজ্যিকভাবে অপারেশন শুরু করে। ডিপিডিসি ৬,৫৫,৯০৮ জন গ্রাহক নিয়ে তার অপারেশন শুরু করে এবং বর্তমানে গ্রাহকের সংখ্যা ১৭,৪৫,৯১৮ (৩১ মার্চ, ২০২৪) এ পৌঁছেছে।<br>
প্রচলিত আইনের কাঠামোর মধ্যে ডিপিডিসির সামগ্রিক পরিচালনার জন্য চূড়ান্ত কর্তৃপক্ষ হলো পরিচালনা পর্ষদ। সরকার কর্তৃক মনোনীত ১২ (বারো) জন পরিচালক দ্বারা বোর্ড গঠিত। পরিচালনা পর্ষদের নির্দেশনা অনুযায়ী, ডিপিডিসি'র কৌশলগত ফাংশন একটি ব্যবস্থাপনা দল দ্বারা পরিচালিত হয় যার প্রধান হলেন ব্যবস্থাপনা পরিচালক ও পাঁচ নির্বাহী পরিচালক (যথাক্রমেঃ নির্বাহী পরিচালক (অপারেশন), নির্বাহী পরিচালক (প্রকৌশল), নির্বাহী পরিচালক (আইসিটি এন্ড প্রকিউরমেন্ট), নির্বাহী পরিচালক (ফাইন্যান্স) ও নির্বাহী পরিচালক (এডমিন এন্ড এইচআর))।"""

}
static_english_messages = {
    "new_meter_document": "To know about the necessary documents for a new meter, <a href='https://dpdc.org.bd/site/nocs/citizen_charter/-' target='_blank'>click here</a>",
    "new_meter_payment": "To know about the demand fee for a new connection, <a href='https://dpdc.org.bd/site/nocs/citizen_charter/-' target='_blank'>click here</a>",
    "new_meter_price": "To know about the demand fee for a new connection, <a href='https://dpdc.org.bd/site/nocs/citizen_charter/-' target='_blank'>click here</a>",
    "new_meter_expected_days": "If the documents are correct, LT connection will be provided within 4 days and HT connection within 15 days. For details, contact our helpline (16116).",
    "new_meter_provider": "For prepaid meters, DPDC will provide the service, and for postpaid meters, customers need to purchase. For details, contact our helpline (16116).",
    "provide_bill_number": "Please provide your bill number.",
    "invalid_bill_number": "No bill found with the provided bill number. Do you want to try with a different bill number?",
    "no_electricity_complaint_registered": "Your complaint has been received, our representative will contact you shortly.",
    "check_meter_balance": "Please check if your meter has sufficient balance.",
    "recharge_for_electricity": "Recharge your meter for uninterrupted electricity service.",
    "not_prepaid_meter": "Your meter is not prepaid. Please contact our helpline (16116).",
    "provide_sequence": "Please provide the sequence code visible on your meter.",
    "provide_customer_number": "Please provide your customer number.",
    "invalid_customer_number": "The customer number you've given isn't in our records. Would you like to try again?<br><br> If you've forgotten your customer number, please reach out to our helpline at (16116).",
    "provide_phone_number": "Please provide your phone number.",
    "invalid_phone_number": "Invalid mobile number. Please contact our helpline (16116).",
    "did_online_register": "Have you applied online?",
    "provide_tracking_number": "Please provide your online application tracking number.",
    "bill_payment_issue": "We sincerely apologize for the inconvenience. Please try again through MFS, Internet Banking, Online Banking, etc. Otherwise, contact our helpline (16116).",
    "retry_tracking_number": "The tracking number provided is incorrect. Please provide the correct tracking number.",
    "invalid_tracking_number": "The tracking number provided is incorrect. Please contact our helpline (16116).",
    "new_registration": "Click on the <a href='https://onlineapplication.dpdc.org.bd/home.php' target='_blank'>application link</a> to apply online",
    "unable_to_reach_dpdc_server": "We sincerely apologize, unable to connect to the server. Please try again later or contact our helpline (16116).",
    "not_found": "We sincerely apologize, We regret to inform you that we're currently unable to address your query. Our chatbot is still undergoing training.<br><br> Please contact our helpline (16116).",
    "call_center_issue": "We sincerely apologize, I'm here to help! Feel free to ask your questions here, and I'll do my best to assist you.",
    "forgot_customer_number": "If you've forgotten your customer number, please contact our customer support at (16116). We'll guide you through the process of recovering it.",
    "for_more_query": "Thank you for using DPDC\'s Chat Support, Please contact our helpline (16116) for any additional queries",
    "confirm_complaint":"Would you like to file a complaint?",
    "confirm_complaint_no_electricity":"We sincerely apologize, Currently there are no scheduled maintenance or interceptions in your area.<br> Would you like to file a complaint?",
    "query_about_customer_number":"Dear customer, Do you know your customer number?",
    "provide_complain_no": "Please provide your tracking number",

    "demand_charge": "Through demand charges, all distribution companies, including DPDC, collect the necessary equipment, materials, and infrastructure construction and maintenance costs from customers for supplying electricity according to the government's directives. Additionally, the government imposes demand charges at a predetermined rate opposite the connected load.",
    "surcharge": "A surcharge (LPS) is an additional fee or charge imposed if the monthly electricity bill is not paid on time as a penalty. The Bangladesh Energy Regulatory Commission imposes a one-time 5% rate for this surcharge.",
    "call_center_info": "16116",
    "vat_query": "Value Added Tax (VAT) is imposed at the government's specified rate. Currently, a 5% VAT is charged for electricity bills.",
    "raise_complaint": "We apologize for any inconvenience. Call DPDC's call center at '16116' to lodge a complaint.",
    "rebate_query": "Rebates are given at a rate of 0.05%.",
    "balance_query": "To know your directory according to your meter, click on 'Prepaid Meter Related Services'.",
    "recharge_commission": "Recharge commission rates vary depending on the amount. For recharge amounts up to 400 Tk, a commission of 5 Tk is charged, for amounts between 401 Tk and 1500 Tk, a commission of 10 Tk is charged, for amounts between 1501 Tk and 5000 Tk, a commission of 15 Tk is charged, and for amounts of 5001 Tk or more, a commission of 25 Tk is charged.",
    "no_bill": "We apologize for any inconvenience. Call DPDC's call center at '16116' to lodge a complaint or contact your respective electricity office.",
    "non_online_recharge": "If your meter is smart or keypad, you can recharge via bKash or Rocket. Soon, all DPDC meters will be converted online.",
    "increase_capacity": "To increase the load on your meter, apply by clicking on 'Citizen Charter' on the DPDC website.",
    "fix_name": "To amend or change your name, apply by clicking <a href='https://onlineapplication.dpdc.org.bd/home.php' target='_blank'>here</a>.",
    "fix_address": "To amend or change your address, apply by clicking <a href='https://onlineapplication.dpdc.org.bd/home.php' target='_blank'>here</a>.",
    "dpdc_website": "<a href='https://dpdc.gov.bd/' target='_blank'>www.dpdc.gov.bd</a>",
    "dpdc_facebook": "<a href='https://facebook.com/dpdcbd' target='_blank'>www.facebook.com/dpdcbd</a>",
    "pay_online": "To pay your bill online, click <a href='https://dpdc.gov.bd/site/page/c3697773-e03c-41ee-b1c8-043d7e7bf1db/-' target='_blank'>here</a> on the DPDC website.",
    "want_prepaid_meter": "All DPDC customers, including your area, will soon be provided with prepaid meters. Thank you for your interest.",
    "solar_panel_requirements": "According to the government's directive, if the approved load for residential customers exceeds 10 kilowatts, solar panels must be installed. Additionally, in the industrial and commercial connection sector, 10% of the total approved load must be installed with solar panels. In both cases, by installing a net meter, customers can support electricity to the national grid and reduce their own bills.",
    "net_metering_query": "To apply for net metering online, visit the Power Division's website <a href='https://powerdivision.gov.bd/' target='_blank'>https://powerdivision.gov.bd</a>.",
    "dpdc_info": "To find information about DPDC staff, click on the link <a href='https://dpdc.org.bd/site/nocs/all_employee' target='_blank'>https://dpdc.org.bd/site/nocs/all_employee</a>.",
    "power_division_complaint_address": "<a href='https://complain.mpemr.gov.bd/' target='_blank'>https://complain.mpemr.gov.bd/</a>",
    "prepaid_meter_rent_query": "Prepaid meters are purchased and installed by DPDC at the rate determined by the government, and a monthly rent is charged. It is noteworthy that if the meter is damaged, DPDC installs a new meter.",
    "tariff_rate_query": "To know the tariff rate, click <a href='https://dpdc.portal.gov.bd/site/page/27e77af7-1187-436c-9f80-b579d3493a46/-' target='_blank'>here</a>.",
    "chatbot_complaint": "I am an artificially intelligent service that has just been activated. I am still learning and training to be a good assistant. Hopefully, I will soon be able to provide all your services efficiently. Thank you for being with DPDC. For more details, call DPDC's call center at '16116'.",
    "service_compliment": "Thank you for your feedback. We will always be there to assist you. For more details, call DPDC's call center at '16116'",
    "electricity_division_call_center_number": "16999",
    "desco_call_center_number": "16120",
    "nocs_address": "For NOCs office address <a href='https://dpdc.org.bd/site/nocs/index_gov/-' target='_blank'>click here</a>",
    "mujibur_rahman_1": "Sheikh Mujibur Rahman, popularly known by the honorific prefix Bangabandhu was a Bangladeshi politician, revolutionary, statesman, activist and diarist.",
    "sheikh_hasina": "Sheikh Hasina Wazed is a Bangladeshi politician who has served as the tenth prime minister of Bangladesh from June 1996 to July 2001 and again since January 2009. She is the daughter of Sheikh Mujibur Rahman, the founding father and first president of Bangladesh",
    "president_of_bangladesh": "Mohammed Shahabuddin Chuppu is a Bangladeshi jurist, civil servant and politician who is the 22nd and current President of Bangladesh. He was elected unopposed in the 2023 presidential election in the nomination of the ruling Awami League.",
    "liberation_war": "The Bangladesh Liberation War, also known as the Bangladesh War of Independence, or simply the Liberation War in Bangladesh, was a revolution and armed conflict sparked by the rise of the Bengali nationalist and self-determination movement in East Pakistan, which resulted in the independence of Bangladesh. ",
    "about_dpdc": "Dhaka Power Distribution Company Limited (DPDC) is a Public Limited Company under the Power Division of the Ministry of Power, Energy and Mineral Resources, Government of Bangladesh, that manages the distribution of electricity to the customers of the Dhaka City Corporation area"

}

confirmation_suggestions = [
    { "english":"Yes", "bangla":"হ্যাঁ" },
    { "english":"No", "bangla":"না" }
]

def static_response_bangla(intent):
    return static_bangla_messages[intent] if intent in static_bangla_messages else static_bangla_messages["not_found"]


def static_response_english(intent):
    return static_english_messages[intent] if intent in static_english_messages else static_english_messages[
        "not_found"]


def find_account(user_input):
    account_number_pattern = r'\b\d{11}\b'
    match = re.search(account_number_pattern, user_input)
    if match:
        return match.group(0)
    else:
        return None


def prepare_reponse(intent, pending_intent, response_bangla, response_english):
    return {
        "intent": intent,
        "pendingIntent": pending_intent,
        "responseBangla": response_bangla,
        "responseEnglish": response_english
    }

def prepare_reponse_with_confirmation(intent, pending_intent, response_bangla, response_english):
    return {
        "intent": intent,
        "pendingIntent": pending_intent,
        "responseBangla": response_bangla,
        "responseEnglish": response_english,
        "suggestions": confirmation_suggestions
    }

def prepare_static_reponse(intent, pending_intent, message_key):
    return {
        "intent": intent,
        "pendingIntent": pending_intent,
        "responseBangla": static_response_bangla(message_key),
        "responseEnglish": static_response_english(message_key)
    }

def prepare_static_reponse_with_confirmation(intent, pending_intent, message_key):
    return {
        "intent": intent,
        "pendingIntent": pending_intent,
        "responseBangla": static_response_bangla(message_key),
        "responseEnglish": static_response_english(message_key),
        "suggestions": confirmation_suggestions

    }
def confirm_customer_number(intent, customer_number):
    return {
        "intent": intent,
        "pendingIntent": "confirm_customer_number",
        "responseBangla": f"আপনি কি '<b>{customer_number}</b>' গ্রাহক নাম্বারের বিপরীতে জিজ্ঞাসা করতে চান?",
        "responseEnglish": f"Would you like to initiate the inquiry using <b>{customer_number}</b>?",
        "suggestions": confirmation_suggestions
    }
def confirm_phone_number(intent, phone_number):
    return {
        "intent": intent,
        "pendingIntent": "confirm_phone_number",
        "responseBangla": f"আপনি কি '<b>{phone_number}</b>' মোবাইল নাম্বারের বিপরীতে জিজ্ঞাসা করতে চান?",
        "responseEnglish": f"Would you like to initiate the inquiry using <b>{phone_number}</b>?",
        "suggestions": confirmation_suggestions
    }
def identify_language(user_input):
    try:
        return detect(user_input)
    except Exception as e:
        return "en"


flow_suggestions =  [
            {"english":"Need one meter", "bangla" : "নতুন সংযোগ নিতে চাই" },
            {"english":"What documents are required for new connection", "bangla" : "নতুন সংযোগ নিতে কি কি কাগজ প্রয়োজন" },
            {"english":"How much will new connection cost", "bangla" : "নতুন সংযোগ নিতে কত টাকা লাগবে" },
            {"english":"No electricity", "bangla" : "বিদ্যুৎ নাই" },
            {"english":"Prepaid meter is not accepting token", "bangla" : "প্রিপেইড মিটার টোকেন নিচ্ছে না" },
            {"english":"Bill is showing due even after payment", "bangla" : "বিল পরিশোধ করার পরেও বকেয়া দেখাচ্ছে" },
            {"english":"Extra Bill", "bangla" : "বিল বেশী আসছে" } 
        ]

def greetings():
    current_time = datetime.datetime.now()
    hour = current_time.hour
    
    message = "How may I help you today?"
    message_bangla = "আজ আপনাকে কীভাবে সাহায্য করতে পারি?"

    if 5 <= hour < 12:
        message = "Good morning! " + message
        message_bangla = "শুভ সকাল! " + message_bangla
    elif 12 <= hour < 17:
        message = "Good afternoon! " + message
        message_bangla = "শুভ বিকাল! " + message_bangla
    elif 17 <= hour < 21:
        message = "Good evening! " + message
        message_bangla = "শুভ সন্ধ্যা! " + message_bangla
    return {
        "intent": "greetings",
        "pendingIntent": None,
        "responseBangla": message_bangla,
        "responseEnglish": message,
        "suggestions": flow_suggestions
    }   


def introduction():
    current_time = datetime.datetime.now()
    hour = current_time.hour
    
    message = "Welcome to DPDC Smart Customer Assistance Chatbot ”বিদ্যুৎ বন্ধু”! How may I help you today?"
    message_bangla = "ডিপিডিসি স্মার্ট কাস্টমার এসিস্ট্যান্ট- চ্যাটবট ”বিদ্যুৎ বন্ধু” তে স্বাগতম! আজ আপনাকে কীভাবে সাহায্য করতে পারি?"

    if 5 <= hour < 12:
        message = "Good morning! " + message
        message_bangla = "শুভ সকাল! " + message_bangla
    elif 12 <= hour < 17:
        message = "Good afternoon! " + message
        message_bangla = "শুভ বিকাল! " + message_bangla
    elif 17 <= hour < 21:
        message = "Good evening! " + message
        message_bangla = "শুভ সন্ধ্যা! " + message_bangla

    return {
        "source": "bot",
        "type": "text",
        "responseBangla": message_bangla,
        "responseEnglish": message,
        "suggestions": flow_suggestions
    }

def continue_asking(): 
    return {
        "intent": "continue_asking",
        "pendingIntent": None,
        "responseBangla": f"নিচের অপশনস থেকে সিলেক্ট করুন অথবা লিখুন",
        "responseEnglish": f"Select from the options below or type",
        "suggestions": flow_suggestions
    }   
def welcome_back():
    current_time = datetime.datetime.now()
    hour = current_time.hour
    
    message = "Welcome to DPDC Smart Customer Assistance Chatbot ”বিদ্যুৎ বন্ধু”! How may I help you today?"
    message_bangla = "ডিপিডিসি স্মার্ট কাস্টমার এসিস্ট্যান্ট- চ্যাটবট ”বিদ্যুৎ বন্ধু” তে স্বাগতম! আজ আপনাকে কীভাবে সাহায্য করতে পারি?"

    if 5 <= hour < 12:
        message = "Good morning! " + message
        message_bangla = "শুভ সকাল! " + message_bangla
    elif 12 <= hour < 17:
        message = "Good afternoon! " + message
        message_bangla = "শুভ বিকাল " + message_bangla
    elif 17 <= hour < 21:
        message = "Good evening! " + message
        message_bangla = "শুভ সন্ধ্যা " + message_bangla
        
    return {
        "source": "bot",
        "type": "text",
        "responseBangla": message_bangla,
        "responseEnglish": message,
        "suggestions": flow_suggestions
    }


def extract_token_number(text):
    pattern = r'Complaint No : (\d+)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return None
    

def make_hyperlink(string):
    print(string)
    # Regular expression pattern to find URLs
    url_pattern = r'https?://\S+'

    # Find URLs in the string
    urls = re.findall(url_pattern, string)

    # Replace URLs with hyperlinks
    for url in urls:
        string = string.replace(url, f'<a href="{url}">{url}</a>')

    return string

def extract_customer_number(message):
    # pattern = re.compile(r'\b\d{8}\b')    
    # match = pattern.search(message)
    # if match:
    #     return match.group()  
    # return None
    pattern = r'\b\d+\b'  # Pattern to match the first sequence of digits in a sentence
    match = re.search(pattern, message)
    if match:
        return match.group(0)
    else:
        return None
    
def extract_phone_number(message):
    pattern = r'\b\d{11}\b'
    match = re.search(pattern, message)
    if match:
        return match.group(0)
    else:
        return None
    
    # pattern = r'\b\d+\b'  # Pattern to match the first sequence of digits in a sentence
    # match = re.search(pattern, message)
    # if match:
    #     return match.group(0)
    # else:
    #     return None
    

def extract_number(message):    
    pattern = r'\b\d+\b'  # Pattern to match the first sequence of digits in a sentence
    match = re.search(pattern, message)
    if match:
        return match.group(0)
    else:
        return None