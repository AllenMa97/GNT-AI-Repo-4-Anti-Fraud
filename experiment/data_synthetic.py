"""
Synthetic Benchmark Dataset
───────────────────────────
10 hand-crafted telecom fraud cases for Layer 1 (public reproducible) evaluation.

Each case contains:
    - case_name, fraud_scenario
    - raw_data: chat records, transactions, app info, call records
    - masked_data: same as raw_data but with all PII masked
    - ground_truth: labels for evaluation

ⓘ These cases are SYNTHETIC — created by the authors for benchmarking purposes.
  No real victim data is included. All names, numbers, and amounts are fictitious.
"""

SYNTHETIC_CASES = [
    # ── Case 00: Investment Scam (投资理财诈骗) ──────────────────────────────
    {
        "case_id": 0,
        "case_name": "Case_00_Investment_Fraud",
        "fraud_scenario": "虚假投资理财诈骗 — Victim lured into fake investment platform via WeChat group",
        "raw_data": {
            "victim_statement": (
                "我在2025年3月通过微信炒股群认识了一个自称是'国信证券高级分析师'的人，"
                "微信昵称是'股市风云-陈老师'。他每天在群里发一些股票分析，看起来很专业。"
                "后来他说有一个私募项目收益很高，让我下载了一个叫'华鑫资本'的APP。"
                "我从3月15日开始，陆续转了5笔钱，总共580,000元。"
                "第一笔转了50,000元到账户6222021001234567890，显示收益涨了20%。"
                "后来客服说要达到VIP等级才能提现，我又转了4笔。"
                "最后一次是4月2日转了200,000元到账户6217002860098765432。"
                "之后APP就打不开了，群里也没人说话了。"
                "我的手机号是13812345678，身份证号是310115199003150012。"
            ),
            "fraud_description": "微信炒股群→下载虚假投资APP→小额试投盈利→诱导大额入金→无法提现→APP关闭",
            "app_type": "虚假投资理财APP",
            "app_name": "华鑫资本",
            "app_description": "仿冒正规券商APP，界面精美，显示虚假收益数据，后台可控",
            "chat_records": [
                {
                    "speaker": "股市风云-陈老师",
                    "message": "各位群友，今天分享一个私募项目，年化收益30%保底，名额有限",
                    "time": "2025-03-10 09:30",
                },
                {
                    "speaker": "投资助理-小林",
                    "message": "陈老师的项目每次都很稳，上期跟投的都赚了至少20%",
                    "time": "2025-03-10 09:32",
                },
                {
                    "speaker": "群友-张投资",
                    "message": "上次跟了20万，半个月就赚了4万多，太爽了",
                    "time": "2025-03-10 09:35",
                },
                {
                    "speaker": "股市风云-陈老师",
                    "message": "大家可以先下载'华鑫资本'APP，用我的邀请码888888注册，新用户送1000元体验金",
                    "time": "2025-03-10 10:00",
                },
                {
                    "speaker": "投资助理-小林",
                    "message": "已下载，界面很专业，和正规券商一样的",
                    "time": "2025-03-10 10:05",
                },
            ],
            "transactions": [
                {"time": "2025-03-15 14:23", "amount": 50000, "direction": "outgoing", "counterparty": "张某某", "counterparty_type": "个人账户", "channel": "手机银行"},
                {"time": "2025-03-18 10:15", "amount": 100000, "direction": "outgoing", "counterparty": "李某某", "counterparty_type": "个人账户", "channel": "手机银行"},
                {"time": "2025-03-22 16:40", "amount": 130000, "direction": "outgoing", "counterparty": "深圳华鑫科技有限公司", "counterparty_type": "对公账户", "channel": "网银"},
                {"time": "2025-03-28 09:20", "amount": 100000, "direction": "outgoing", "counterparty": "深圳华鑫科技有限公司", "counterparty_type": "对公账户", "channel": "网银"},
                {"time": "2025-04-02 11:05", "amount": 200000, "direction": "outgoing", "counterparty": "王某某", "counterparty_type": "个人账户", "channel": "手机银行"},
            ],
            "call_records": [
                {"time": "2025-03-16 15:00", "duration": 180, "direction": "incoming", "caller": "投资助理-小林"},
                {"time": "2025-03-25 10:30", "duration": 120, "direction": "incoming", "caller": "客服"},
                {"time": "2025-04-01 14:00", "duration": 300, "direction": "incoming", "caller": "陈老师"},
            ],
            "latest_transaction": {"amount": 200000, "minutes_ago": 60},
        },
        "ground_truth": {
            "fraud_type": "investment_fraud",
            "fraud_subtype": "虚假理财APP",
            "entities": [
                {"type": "suspect", "value": "股市风云-陈老师", "role": "主犯/讲师"},
                {"type": "suspect", "value": "投资助理-小林", "role": "托/助理"},
                {"type": "suspect", "value": "群友-张投资", "role": "托"},
                {"type": "platform", "value": "华鑫资本", "role": "虚假APP"},
                {"type": "account", "value": "[银行卡号_1]", "role": "一级收款"},
                {"type": "account", "value": "[银行卡号_2]", "role": "二级收款"},
            ],
            "fund_flow": {
                "total_outflow": 580000,
                "total_inflow": 0,
                "chain": "受害人→张某某(5万)→李某某(10万)→深圳华鑫科技(23万)→深圳华鑫科技(10万)→王某某(20万)",
            },
            "timeline_phases": ["引流", "通联", "网络", "交易"],
            "quality_issues": [
                "Missing APP forensic analysis",
                "Missing suspect IP/location data",
                "Incomplete chat log (only 5 messages)",
            ],
            "recommendations": [
                "立即对涉案银行卡进行紧急止付",
                "提取华鑫资本APP进行电子取证",
                "通过资金链路追踪嫌疑人身份",
            ],
        },
    },

    # ── Case 01: Romance Scam (杀猪盘) ────────────────────────────────────
    {
        "case_id": 1,
        "case_name": "Case_01_Romance_Scam",
        "fraud_scenario": "杀猪盘诈骗 — Victim develops online relationship, then lured into fake gambling platform",
        "raw_data": {
            "victim_statement": (
                "我在2025年2月在陌陌上认识了一个叫'雨落倾城'的女生，聊了大概一个月后感情升温，"
                "她自称在深圳做外贸，单身。后来她说她舅舅在澳门赌场工作，知道一个博彩网站的漏洞，"
                "可以在特定时间下注稳赢。她让我下载一个叫'永利国际'的APP。"
                "我先充了3000元试水，确实赚了2000提出来了。后来她一直催我多充，说机会难得。"
                "我又陆续充了8万、15万、12万，总共转出353,000元。"
                "当我想要全部提出时，客服说要交20%的保证金才能提。"
                "我再联系她就联系不上了。我的身份证号是440305198807150034。"
            ),
            "fraud_description": "社交软件结识→建立感情→诱导参与博彩→小额返利→大额诈骗→无法提现→失联",
            "app_type": "虚假博彩平台",
            "app_name": "永利国际",
            "app_description": "仿冒澳门赌场品牌，后台可操控开奖结果，前期让受害者小赢，后期操控赔率",
            "chat_records": [
                {"speaker": "雨落倾城", "message": "小哥哥，你在干嘛呢？我刚下班好累呀", "time": "2025-02-20 19:30"},
                {"speaker": "雨落倾城", "message": "告诉你一个秘密，我舅舅在澳门永利工作，他知道一个赔率漏洞", "time": "2025-03-05 21:00"},
                {"speaker": "雨落倾城", "message": "我昨天帮朋友投了5万，两个小时就赚了3万多，但机会只有今天晚上了", "time": "2025-03-08 20:30"},
                {"speaker": "雨落倾城", "message": "你相信我，我不会害你的，我已经把你当最亲的人了", "time": "2025-03-08 20:35"},
                {"speaker": "雨落倾城", "message": "你再加50万吧，这次稳赚，错过了就再也没机会了", "time": "2025-03-20 15:00"},
            ],
            "transactions": [
                {"time": "2025-03-09 20:15", "amount": 3000, "direction": "outgoing", "counterparty": "永利国际", "counterparty_type": "平台账户", "channel": "支付宝"},
                {"time": "2025-03-10 09:30", "amount": -5000, "direction": "incoming", "counterparty": "永利国际", "counterparty_type": "平台账户", "channel": "支付宝"},
                {"time": "2025-03-15 14:20", "amount": 80000, "direction": "outgoing", "counterparty": "赵某某", "counterparty_type": "个人账户", "channel": "手机银行"},
                {"time": "2025-03-18 10:45", "amount": 150000, "direction": "outgoing", "counterparty": "刘某某", "counterparty_type": "个人账户", "channel": "手机银行"},
                {"time": "2025-03-22 16:30", "amount": 120000, "direction": "outgoing", "counterparty": "陈某某", "counterparty_type": "个人账户", "channel": "网银"},
            ],
            "call_records": [
                {"time": "2025-03-08 21:00", "duration": 600, "direction": "incoming", "caller": "雨落倾城"},
                {"time": "2025-03-20 14:30", "duration": 420, "direction": "incoming", "caller": "雨落倾城"},
            ],
            "latest_transaction": {"amount": 120000, "minutes_ago": 120},
        },
        "ground_truth": {
            "fraud_type": "romance_scam",
            "fraud_subtype": "杀猪盘-博彩类",
            "entities": [
                {"type": "suspect", "value": "雨落倾城", "role": "话务员/感情诱导"},
                {"type": "platform", "value": "永利国际", "role": "虚假博彩APP"},
                {"type": "platform", "value": "陌陌", "role": "引流渠道"},
            ],
            "fund_flow": {"total_outflow": 353000, "total_inflow": 5000, "chain": "受害人→永利国际(3k)→返利(5k)→赵某某(8万)→刘某某(15万)→陈某某(12万)"},
            "timeline_phases": ["引流", "通联", "网络", "交易"],
            "quality_issues": ["Missing social app account forensic data", "Missing suspect phone location records"],
            "recommendations": ["追踪'雨落倾城'注册IP及设备指纹", "分析永利国际APP后端服务器地址"],
        },
    },

    # ── Case 02: Impersonating Customer Service (冒充客服) ───────────────
    {
        "case_id": 2,
        "case_name": "Case_02_Impersonate_Customer_Service",
        "fraud_scenario": "冒充客服诈骗 — Fake courier/taobao customer service claiming lost package refund",
        "raw_data": {
            "victim_statement": (
                "2025年4月5日，我接到一个电话，号码是+852-12345678，对方自称是顺丰快递客服，"
                "说我的快递在运输途中丢失了，要给我双倍赔偿。他准确说出了我的快递单号和收货地址。"
                "然后他让我加一个QQ号（昵称：顺丰理赔中心），加了之后发了一个链接让我填银行卡信息。"
                "我填了银行卡号6228480030123456789和验证码。"
                "之后发现卡里的98,000元被转走了。"
                "我的手机号是13798765432，身份证号是330106199502280021。"
            ),
            "fraud_description": "冒充快递客服→准确说出订单信息→诱导加QQ→钓鱼链接→窃取银行卡密码→盗刷",
            "app_type": "无（电话+QQ+钓鱼网页）",
            "app_name": "钓鱼链接",
            "app_description": "仿冒快递理赔页面，要求输入银行卡号、密码、验证码",
            "chat_records": [
                {"speaker": "顺丰理赔中心", "message": "您的快递单号SF1234567890123，在运输途中出现异常，我们深感抱歉", "time": "2025-04-05 14:00"},
                {"speaker": "顺丰理赔中心", "message": "请点击以下链接填写理赔信息：http://sf-claim.top/form", "time": "2025-04-05 14:01"},
                {"speaker": "顺丰理赔中心", "message": "请务必在30分钟内完成，否则理赔通道将关闭", "time": "2025-04-05 14:03"},
            ],
            "transactions": [
                {"time": "2025-04-05 14:30", "amount": 98000, "direction": "outgoing", "counterparty": "周某某", "counterparty_type": "个人账户", "channel": "手机银行"},
            ],
            "call_records": [
                {"time": "2025-04-05 13:55", "duration": 240, "direction": "incoming", "caller": "+852-12345678"},
            ],
            "latest_transaction": {"amount": 98000, "minutes_ago": 30},
        },
        "ground_truth": {
            "fraud_type": "impersonate_customer_service",
            "fraud_subtype": "冒充快递客服",
            "entities": [
                {"type": "suspect", "value": "顺丰理赔中心", "role": "冒充客服"},
                {"type": "phone", "value": "+852-12345678", "role": "诈骗电话"},
                {"type": "url", "value": "http://sf-claim.top", "role": "钓鱼网站"},
            ],
            "fund_flow": {"total_outflow": 98000, "total_inflow": 0, "chain": "受害人→周某某(98k)"},
            "timeline_phases": ["通联", "交易"],
            "quality_issues": ["Missing phishing URL forensic capture", "Missing telecom carrier CDR data"],
            "recommendations": ["紧急止付周某某账户", "提取钓鱼网站服务器信息"],
        },
    },

    # ── Case 03: Task-Brushing Scam (刷单诈骗) ───────────────────────────
    {
        "case_id": 3,
        "case_name": "Case_03_Task_Brushing_Scam",
        "fraud_scenario": "刷单返利诈骗 — Victim recruited via SMS for 'part-time task' earning commissions",
        "raw_data": {
            "victim_statement": (
                "2025年5月，我收到一条短信说可以做兼职刷单，每天赚200-500元。"
                "我加了短信里的QQ群，群主'任务管理-王经理'让我下载一个叫'任务宝'的APP。"
                "刚开始做了几个小任务，关注微信公众号，每个给5元钱，都按时结算了。"
                "后来让我做垫付任务，垫1000返1200，垫3000返3600。"
                "我慢慢垫到了10000元，但客服说我操作失误导致账户冻结，需要充20000元解冻。"
                "我又充了20000元，还是不能提，说需要再充50000元升级VIP。"
                "总共被骗了145,000元。我身份证号是35020319910918123X。"
            ),
            "fraud_description": "短信引流→加QQ群→下载刷单APP→小额返利建立信任→垫付任务→虚假冻结→充值解冻→无法提现",
            "app_type": "虚假刷单平台",
            "app_name": "任务宝",
            "app_description": "仿冒兼职接单平台，展示虚假任务和收益，后台操控账户状态",
            "chat_records": [
                {"speaker": "任务管理-王经理", "message": "欢迎加入！新人先做关注任务，关注3个公众号领15元", "time": "2025-05-10 09:00"},
                {"speaker": "任务管理-王经理", "message": "现在有垫付任务，垫1000返1200，名额有限", "time": "2025-05-11 10:00"},
                {"speaker": "任务管理-王经理", "message": "您操作失误导致账户异常，需要充值20000元解冻", "time": "2025-05-13 14:00"},
            ],
            "transactions": [
                {"time": "2025-05-11 10:30", "amount": 1000, "direction": "outgoing", "counterparty": "孙某某", "counterparty_type": "个人账户", "channel": "微信"},
                {"time": "2025-05-11 12:00", "amount": -1200, "direction": "incoming", "counterparty": "孙某某", "counterparty_type": "个人账户", "channel": "微信"},
                {"time": "2025-05-12 09:15", "amount": 3000, "direction": "outgoing", "counterparty": "吴某某", "counterparty_type": "个人账户", "channel": "微信"},
                {"time": "2025-05-12 11:00", "amount": -3600, "direction": "incoming", "counterparty": "吴某某", "counterparty_type": "个人账户", "channel": "微信"},
                {"time": "2025-05-13 10:00", "amount": 10000, "direction": "outgoing", "counterparty": "郑某某", "counterparty_type": "个人账户", "channel": "手机银行"},
                {"time": "2025-05-13 15:00", "amount": 20000, "direction": "outgoing", "counterparty": "郑某某", "counterparty_type": "个人账户", "channel": "手机银行"},
                {"time": "2025-05-15 09:00", "amount": 50000, "direction": "outgoing", "counterparty": "钱某某", "counterparty_type": "个人账户", "channel": "网银"},
                {"time": "2025-05-16 10:00", "amount": 65000, "direction": "outgoing", "counterparty": "钱某某", "counterparty_type": "个人账户", "channel": "网银"},
            ],
            "call_records": [],
            "latest_transaction": {"amount": 65000, "minutes_ago": 45},
        },
        "ground_truth": {
            "fraud_type": "task_brushing_scam",
            "fraud_subtype": "刷单返利诈骗",
            "entities": [
                {"type": "suspect", "value": "任务管理-王经理", "role": "群主/话务员"},
                {"type": "platform", "value": "任务宝", "role": "虚假刷单APP"},
            ],
            "fund_flow": {"total_outflow": 149000, "total_inflow": 4800, "chain": "受害人→孙(1k)→返1.2k→吴(3k)→返3.6k→郑(10k)→郑(20k)→钱(50k)→钱(65k)"},
            "timeline_phases": ["引流", "通联", "网络", "交易"],
            "quality_issues": ["Missing SMS gateway trace", "Missing QQ group member analysis"],
            "recommendations": ["紧急止付钱某某账户", "追踪短信发送网关"],
        },
    },

    # ── Case 04: Fake Credit (虚假征信诈骗) ─────────────────────────────
    {
        "case_id": 4,
        "case_name": "Case_04_Fake_Credit_Scam",
        "fraud_scenario": "虚假征信诈骗 — Victim told their credit score has issues, must transfer money to 'secure account'",
        "raw_data": {
            "victim_statement": (
                "2025年6月接到电话，对方自称是'京东金融客服'，说我的京东金条账户异常，"
                "如果不处理会影响个人征信。对方让我下载'云会议'APP进行屏幕共享操作。"
                "他引导我在多个网贷平台借款，然后让我把所有钱转到'银保监会安全账户'。"
                "我先后在借呗、微粒贷、招联金融借了120000元、80000元、100000元，"
                "全部转到了指定账户6214830112345678900。"
                "后来回拨电话就打不通了。身份证号是120103198512150032。"
            ),
            "fraud_description": "冒充金融机构客服→制造征信焦虑→屏幕共享→诱导网贷→转入'安全账户'",
            "app_type": "屏幕共享APP+多个正规网贷平台（被利用）",
            "app_name": "云会议",
            "app_description": "正规远程会议软件，被诈骗分子利用来进行屏幕共享，获取受害者银行卡信息和操作权限",
            "chat_records": [],
            "transactions": [
                {"time": "2025-06-10 14:00", "amount": 120000, "direction": "outgoing", "counterparty": "冯某某", "counterparty_type": "个人账户", "channel": "手机银行"},
                {"time": "2025-06-10 15:30", "amount": 80000, "direction": "outgoing", "counterparty": "冯某某", "counterparty_type": "个人账户", "channel": "手机银行"},
                {"time": "2025-06-10 16:45", "amount": 100000, "direction": "outgoing", "counterparty": "冯某某", "counterparty_type": "个人账户", "channel": "手机银行"},
            ],
            "call_records": [
                {"time": "2025-06-10 10:00", "duration": 900, "direction": "incoming", "caller": "+86-17312345678"},
                {"time": "2025-06-10 13:30", "duration": 1800, "direction": "incoming", "caller": "+86-17312345678"},
            ],
            "latest_transaction": {"amount": 100000, "minutes_ago": 75},
        },
        "ground_truth": {
            "fraud_type": "fake_credit_scam",
            "fraud_subtype": "虚假征信-注销校园贷/金条类",
            "entities": [
                {"type": "suspect", "value": "+86-17312345678", "role": "冒充京东客服"},
                {"type": "account", "value": "[银行卡号_1]", "role": "收款账户"},
            ],
            "fund_flow": {"total_outflow": 300000, "total_inflow": 0, "chain": "受害人（借呗12万+微粒贷8万+招联10万）→冯某某(30万)"},
            "timeline_phases": ["通联", "交易"],
            "quality_issues": ["Missing screen recording forensic data", "Missing网贷 platform account audit trail"],
            "recommendations": ["紧急止付冯某某账户", "获取云会议通话记录"],
        },
    },

    # ── Case 05: Loan Scam (贷款诈骗) ───────────────────────────────────
    {
        "case_id": 5,
        "case_name": "Case_05_Loan_Scam",
        "fraud_scenario": "贷款诈骗 — Victim applies for quick loan, trapped by 'deposit/fee' scheme",
        "raw_data": {
            "victim_statement": (
                "2025年1月我收到一条短信，说'您已获得20万额度，日息万分之三，点击链接申请'。"
                "我点了链接下载了'极速贷'APP，填写了身份信息和银行卡号。"
                "申请后系统显示'审核通过'但是要交6000元的'解冻费'才能提款。"
                "我交了6000元后，客服说我的银行卡号填错了，需要再交15000元'改卡费'。"
                "我又交了15000元。然后客服说需要交30000元的'保证金'证明还款能力。"
                "前后交了51000元也没拿到贷款。身份证号是610113197803210015。"
            ),
            "fraud_description": "短信广告→下载虚假贷款APP→填写信息→审核通过→各种名目收费→永不发放贷款",
            "app_type": "虚假贷款APP",
            "app_name": "极速贷",
            "app_description": "仿冒正规贷款APP界面，后台显示虚假审核结果，收取各种费用后永不发放",
            "chat_records": [
                {"speaker": "客服-小李", "message": "您的20万贷款已审核通过！但需要先缴纳6000元解冻费", "time": "2025-01-20 10:00"},
                {"speaker": "客服-小李", "message": "您填写的银行卡号有误，导致资金冻结，需要缴纳15000元改卡费", "time": "2025-01-20 11:00"},
                {"speaker": "客服-小李", "message": "还需要缴纳30000元保证金证明您的还款能力，放款后全额退还", "time": "2025-01-20 14:00"},
            ],
            "transactions": [
                {"time": "2025-01-20 10:15", "amount": 6000, "direction": "outgoing", "counterparty": "何某某", "counterparty_type": "个人账户", "channel": "微信"},
                {"time": "2025-01-20 11:30", "amount": 15000, "direction": "outgoing", "counterparty": "何某某", "counterparty_type": "个人账户", "channel": "微信"},
                {"time": "2025-01-20 14:30", "amount": 30000, "direction": "outgoing", "counterparty": "吕某某", "counterparty_type": "个人账户", "channel": "手机银行"},
            ],
            "call_records": [],
            "latest_transaction": {"amount": 30000, "minutes_ago": 30},
        },
        "ground_truth": {
            "fraud_type": "loan_scam",
            "fraud_subtype": "虚假贷款-收取费用类",
            "entities": [
                {"type": "suspect", "value": "客服-小李", "role": "话务员"},
                {"type": "platform", "value": "极速贷", "role": "虚假贷款APP"},
            ],
            "fund_flow": {"total_outflow": 51000, "total_inflow": 0, "chain": "受害人→何某某(6k+15k)→吕某某(30k)"},
            "timeline_phases": ["引流", "通联", "网络", "交易"],
            "quality_issues": ["Missing SMS sender trace", "Missing APK forensic analysis"],
            "recommendations": ["提取极速贷APP进行逆向分析", "追踪何某某、吕某某账户"],
        },
    },

    # ── Case 06: Government Impersonation (冒充公检法) ──────────────────
    {
        "case_id": 6,
        "case_name": "Case_06_Government_Impersonation",
        "fraud_scenario": "冒充公检法诈骗 — Victim told they're involved in a criminal case, must transfer funds for 'investigation'",
        "raw_data": {
            "victim_statement": (
                "2025年7月我接到一个电话，对方自称是'北京市公安局刑侦总队'的民警，警号013245，"
                "说我的银行卡涉嫌洗钱，已经被最高检列入调查名单。"
                "他让我加了一个QQ，发了一张'刑事逮捕令'和'资金冻结令'的照片，上面有我的照片和身份证号。"
                "然后他说需要我把所有存款转入'安全账户'接受审查，审查完会返还。"
                "我非常害怕，按照他的指示把350,000元存款全部转了过去。"
                "后来才发现被骗。身份证号是32050119651203001X。"
            ),
            "fraud_description": "冒充警察→制造恐慌（洗钱/逮捕）→发送伪造法律文书→要求转账到'安全账户'",
            "app_type": "无（电话+QQ+伪造文书）",
            "app_name": "伪造逮捕令",
            "app_description": "PS制作的虚假法律文书（刑事逮捕令、资金冻结令），包含受害者真实身份信息",
            "chat_records": [
                {"speaker": "北京刑侦-王警官", "message": "你好，我是北京市公安局刑侦总队王建国，警号013245，你的银行卡涉嫌洗钱", "time": "2025-07-05 09:00"},
                {"speaker": "北京刑侦-王警官", "message": "这是你的刑事逮捕令和资金冻结令，请确认是否本人", "time": "2025-07-05 09:05"},
                {"speaker": "北京刑侦-王警官", "message": "现在你需要将所有资金转移到安全账户接受审查，审查期24小时，结束后全额返还", "time": "2025-07-05 09:30"},
                {"speaker": "北京刑侦-王警官", "message": "这件事情不能告诉任何人，包括家人和本地公安局，否则会影响案件侦办", "time": "2025-07-05 09:35"},
            ],
            "transactions": [
                {"time": "2025-07-05 11:00", "amount": 350000, "direction": "outgoing", "counterparty": "马某某", "counterparty_type": "个人账户", "channel": "柜台转账"},
            ],
            "call_records": [
                {"time": "2025-07-05 08:55", "duration": 480, "direction": "incoming", "caller": "+86-010-87654321"},
                {"time": "2025-07-05 10:30", "duration": 360, "direction": "incoming", "caller": "+86-010-87654321"},
            ],
            "latest_transaction": {"amount": 350000, "minutes_ago": 60},
        },
        "ground_truth": {
            "fraud_type": "government_impersonation",
            "fraud_subtype": "冒充公检法",
            "entities": [
                {"type": "suspect", "value": "北京刑侦-王警官", "role": "冒充警察"},
                {"type": "suspect", "value": "+86-010-87654321", "role": "诈骗电话（GOIP改号）"},
            ],
            "fund_flow": {"total_outflow": 350000, "total_inflow": 0, "chain": "受害人→柜台转账→马某某(35万)"},
            "timeline_phases": ["通联", "交易"],
            "quality_issues": ["Missing telecom carrier trunk trace", "Missing forged document forensics"],
            "recommendations": ["紧急止付马某某账户", "追踪GOIP设备位置"],
        },
    },

    # ── Case 07: Grandparent Scam (冒充熟人-老年人类) ─────────────────
    {
        "case_id": 7,
        "case_name": "Case_07_Grandparent_Scam",
        "fraud_scenario": "冒充熟人诈骗 — Victim's 'grandchild' calls saying they're in trouble, needs money urgently",
        "raw_data": {
            "victim_statement": (
                "2025年8月3日下午，我接到一个电话，对方喊我'爷爷'，说他在外面跟人打架把人打伤了，"
                "现在被派出所抓了，需要8万元赔偿对方才能私了。"
                "电话里声音很像我的孙子小陈。他说不能告诉他爸妈，怕被骂。"
                "他让他的'同学'来接我去银行取钱。我在柜台取了80000元现金给了那个年轻人。"
                "后来我打电话给我孙子，他说根本没这回事。我身份证号是440102194508150011。"
            ),
            "fraud_description": "冒充孙子/外孙→编造紧急情况→利用老人护孙心切→线下取现交接→现金交付",
            "app_type": "无（电话诈骗+线下取现）",
            "app_name": "无",
            "app_description": "纯电话诈骗，不涉及APP。诈骗分子利用老年人信息闭塞、护亲情切的特点",
            "chat_records": [],
            "transactions": [
                {"time": "2025-08-03 15:00", "amount": 80000, "direction": "outgoing", "counterparty": "现金取款", "counterparty_type": "现金", "channel": "柜台取现"},
            ],
            "call_records": [
                {"time": "2025-08-03 14:00", "duration": 180, "direction": "incoming", "caller": "+86-13800000000"},
                {"time": "2025-08-03 14:30", "duration": 60, "direction": "incoming", "caller": "+86-13800000001"},
            ],
            "latest_transaction": {"amount": 80000, "minutes_ago": 30},
        },
        "ground_truth": {
            "fraud_type": "impersonate_acquaintance",
            "fraud_subtype": "冒充熟人-晚辈类",
            "entities": [
                {"type": "suspect", "value": "+86-13800000000", "role": "冒充孙子"},
            ],
            "fund_flow": {"total_outflow": 80000, "total_inflow": 0, "chain": "受害人→柜台取现→交付'同学'→现金消失"},
            "timeline_phases": ["通联", "交易"],
            "quality_issues": ["Missing bank CCTV footage", "Missing cash handler description"],
            "recommendations": ["调取银行柜台监控录像", "追踪取款人行动轨迹"],
        },
    },

    # ── Case 08: Prize Scam (中奖诈骗) ─────────────────────────────────
    {
        "case_id": 8,
        "case_name": "Case_08_Prize_Scam",
        "fraud_scenario": "中奖诈骗 — Victim receives message about winning a prize, must pay 'tax' first",
        "raw_data": {
            "victim_statement": (
                "我2025年9月在刷抖音时收到一条私信，说我在'抖音年度抽奖'中了二等奖，"
                "奖品是一台iPhone 16 Pro Max和5万元现金。"
                "对方让我加一个QQ号联系'领奖客服'。客服说领奖需要先交'个人所得税'2000元。"
                "我交了2000元后，客服又说需要交3000元的'公证费'。"
                "接着又说要交5000元的'保证金'。前后交了10000元，什么也没收到。"
                "身份证号是320106199006150022。"
            ),
            "fraud_description": "社交平台私信→中奖通知→加客服→层层收费（个税/公证费/保证金）→拉黑",
            "app_type": "无（抖音+QQ）",
            "app_name": "抖音",
            "app_description": "正规平台被诈骗分子用私信/评论功能进行引流",
            "chat_records": [
                {"speaker": "抖音抽奖中心", "message": "恭喜！您在抖音年度抽奖中获得二等奖：iPhone 16 Pro Max + 50000元现金！", "time": "2025-09-10 10:00"},
                {"speaker": "领奖客服-小陈", "message": "请先缴纳2000元个人所得税，缴纳后立即发放奖品", "time": "2025-09-10 10:30"},
                {"speaker": "领奖客服-小陈", "message": "还需要缴纳3000元公证费，这是领奖的必要手续", "time": "2025-09-10 11:00"},
                {"speaker": "领奖客服-小陈", "message": "最后再缴纳5000元保证金，保证金在领奖后退还", "time": "2025-09-10 14:00"},
            ],
            "transactions": [
                {"time": "2025-09-10 10:40", "amount": 2000, "direction": "outgoing", "counterparty": "黄某某", "counterparty_type": "个人账户", "channel": "微信"},
                {"time": "2025-09-10 11:15", "amount": 3000, "direction": "outgoing", "counterparty": "黄某某", "counterparty_type": "个人账户", "channel": "微信"},
                {"time": "2025-09-10 14:30", "amount": 5000, "direction": "outgoing", "counterparty": "曹某某", "counterparty_type": "个人账户", "channel": "支付宝"},
            ],
            "call_records": [],
            "latest_transaction": {"amount": 5000, "minutes_ago": 90},
        },
        "ground_truth": {
            "fraud_type": "prize_scam",
            "fraud_subtype": "中奖诈骗-虚假抽奖类",
            "entities": [
                {"type": "suspect", "value": "领奖客服-小陈", "role": "话务员"},
            ],
            "fund_flow": {"total_outflow": 10000, "total_inflow": 0, "chain": "受害人→黄某某(2k+3k)→曹某某(5k)"},
            "timeline_phases": ["引流", "通联", "交易"],
            "quality_issues": ["Missing抖音 account audit trail", "Missing payment platform account info"],
            "recommendations": ["追踪抖音私信发送账号", "调取黄某某、曹某某微信/支付宝实名信息"],
        },
    },

    # ── Case 09: Pig-Butchering Variant (杀猪盘变体-虚拟货币) ──────────
    {
        "case_id": 9,
        "case_name": "Case_09_Pig_Butchering_Crypto",
        "fraud_scenario": "杀猪盘变体 — Victim lured into fake cryptocurrency trading platform",
        "raw_data": {
            "victim_statement": (
                "2025年10月，我在探探上认识了一个自称在迪拜做区块链的男生，微信昵称'区块链-大卫'。"
                "聊了两周后，他让我下载一个叫'BTX星际交易所'的APP，说他有内部消息知道哪只币会涨。"
                "我先充了5000USDT（约35000元人民币），在他的指导下操作确实盈利了。"
                "他让我加大投入，说这次有重大利好。"
                "我又分3次充了20000USDT、30000USDT、50000USDT，总共投入约735,000元人民币。"
                "当我想提现的时候，平台显示'系统维护中'，再之后APP打不开了。"
                "他也把我拉黑了。身份证号是310107199204080012。"
            ),
            "fraud_description": "探探交友→建立感情→诱导下载虚假交易所→USDT入金→小赚取信→大额投入→无法提现→失联",
            "app_type": "虚假加密货币交易所",
            "app_name": "BTX星际交易所",
            "app_description": "仿冒加密货币交易所，显示虚假行情，后台操控价格走势，控制提现功能",
            "chat_records": [
                {"speaker": "区块链-大卫", "message": "美女你好，你也在关注区块链吗？我在迪拜做量化交易", "time": "2025-10-05 20:00"},
                {"speaker": "区块链-大卫", "message": "我有个内部消息，BTC今晚会大涨，建议你跟我一起做多", "time": "2025-10-12 19:00"},
                {"speaker": "区块链-大卫", "message": "这次是千载难逢的机会，机构资金马上进场，至少翻倍", "time": "2025-10-18 15:00"},
                {"speaker": "区块链-大卫", "message": "你信我，我不会害你，我们已经这么熟了", "time": "2025-10-20 21:00"},
            ],
            "transactions": [
                {"time": "2025-10-15 14:00", "amount": 5000, "direction": "outgoing", "counterparty": "BTX交易所", "counterparty_type": "USDT地址", "channel": "加密货币"},
                {"time": "2025-10-20 10:00", "amount": 20000, "direction": "outgoing", "counterparty": "BTX交易所", "counterparty_type": "USDT地址", "channel": "加密货币"},
                {"time": "2025-10-22 16:00", "amount": 30000, "direction": "outgoing", "counterparty": "BTX交易所", "counterparty_type": "USDT地址", "channel": "加密货币"},
                {"time": "2025-10-25 11:00", "amount": 50000, "direction": "outgoing", "counterparty": "BTX交易所", "counterparty_type": "USDT地址", "channel": "加密货币"},
            ],
            "call_records": [
                {"time": "2025-10-19 20:30", "duration": 900, "direction": "incoming", "caller": "区块链-大卫"},
            ],
            "latest_transaction": {"amount": 50000, "minutes_ago": 30},
        },
        "ground_truth": {
            "fraud_type": "romance_scam",
            "fraud_subtype": "杀猪盘-虚拟货币类",
            "entities": [
                {"type": "suspect", "value": "区块链-大卫", "role": "话务员/感情诱导"},
                {"type": "platform", "value": "BTX星际交易所", "role": "虚假加密货币交易所"},
                {"type": "platform", "value": "探探", "role": "引流渠道"},
            ],
            "fund_flow": {"total_outflow": 735000, "total_inflow": 0, "chain": "受害人→USDT充币→BTX交易所→嫌疑人控制的链上地址"},
            "timeline_phases": ["引流", "通联", "网络", "交易"],
            "quality_issues": ["Missing blockchain transaction forensics", "Missing APP APK analysis"],
            "recommendations": ["对BTX交易所域名和IP进行溯源", "追踪USDT链上流转路径"],
        },
    },
]


# ─── Utility ──────────────────────────────────────────────────────────────────

def get_case_by_id(case_id: int) -> dict:
    """Get a synthetic case by ID (0-9)."""
    for case in SYNTHETIC_CASES:
        if case["case_id"] == case_id:
            return case
    raise ValueError(f"Case {case_id} not found")

def list_cases() -> list:
    """List all available synthetic cases."""
    return [
        {"id": c["case_id"], "name": c["case_name"], "scenario": c["fraud_scenario"]}
        for c in SYNTHETIC_CASES
    ]
