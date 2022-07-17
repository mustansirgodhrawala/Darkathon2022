import os

files = [
    "20808925.html",
    "16107710.html",
    "17080036.html",
    "25658216.html",
    "19693249.html",
    "27548314.html",
    "26389668.html",
    "21959917.html",
    "29546148.html",
    "25100526.html",
    "16249428.html",
    "17389922.html",
    "9041215.html",
    "25848341.html",
    "21716590.html",
    "6938607.html",
    "22872766.html",
    "25207149.html",
    "29144438.html",
    "17320771.html",
    "19718853.html",
    "14975666.html",
    "11629622.html",
    "15563653.html",
    "11952201.html",
    "10766714.html",
    "24049455.html",
    "17764735.html",
    "22319916.html",
    "21909333.html",
    "25075221.html",
    "10811240.html",
    "26437590.html",
    "22475990.html",
    "16311031.html",
    "20155309.html",
    "22099412.html",
    "16527729.html",
    "5343281.html",
    "6021756.html",
    "19726754.html",
    "13555717.html",
    "20899350.html",
    "8058394.html",
    "18780147.html",
    "12336303.html",
    "12043588.html",
    "6667615.html",
    "9003301.html",
    "28917706.html",
    "14875059.html",
    "9771497.html",
    "22744629.html",
    "7002162.html",
    "9058344.html",
    "6672610.html",
    "23107863.html",
    "23377443.html",
    "24181685.html",
    "25343927.html",
    "18880340.html",
    "5172813.html",
    "6216938.html",
    "8129031.html",
    "28010768.html",
    "9645644.html",
    "15479879.html",
    "23576179.html",
    "8531428.html",
    "29130496.html",
    "29567442.html",
    "11212636.html",
    "10802542.html",
    "12803635.html",
    "18192428.html",
    "6411209.html",
    "28894868.html",
    "8228985.html",
    "25426183.html",
    "23116321.html",
    "13879407.html",
    "19605158.html",
    "25609349.html",
    "21157566.html",
    "23009523.html",
    "11540609.html",
    "8248835.html",
    "13580445.html",
    "29139625.html",
    "12645586.html",
    "11897957.html",
    "5597959.html",
    "5794956.html",
    "11614314.html",
    "11371525.html",
    "5166723.html",
    "20733064.html",
    "5618861.html",
    "10488839.html",
    "18553719.html",
    "13998636.html",
    "24769576.html",
    "8618314.html",
    "24970804.html",
    "11113511.html",
    "22953274.html",
    "7213784.html",
    "6716242.html",
    "16145829.html",
    "14068768.html",
    "24889703.html",
    "7533855.html",
    "26610905.html",
    "22592758.html",
    "29505613.html",
    "25617027.html",
    "7880635.html",
    "29729093.html",
    "8227656.html",
    "27910053.html",
    "13664793.html",
    "18906945.html",
    "14696870.html",
    "17323152.html",
    "24862437.html",
    "28428489.html",
    "14011373.html",
    "27824175.html",
    "18058048.html",
    "25239050.html",
    "26334549.html",
    "5867711.html",
    "8839464.html",
    "17009588.html",
    "21535517.html",
    "16531628.html",
    "13826315.html",
    "27817543.html",
    "15661808.html",
    "5676987.html",
    "26708108.html",
    "16314517.html",
    "23119917.html",
    "24184163.html",
    "18741214.html",
    "28994159.html",
    "29498860.html",
    "29824955.html",
    "18563682.html",
    "10544297.html",
    "27549564.html",
    "9376744.html",
    "6445548.html",
    "13210834.html",
    "6276467.html",
    "16065016.html",
    "29741590.html",
    "9802086.html",
    "22382457.html",
    "10689076.html",
    "10424868.html",
    "11719844.html",
    "13125908.html",
    "21151532.html",
    "7536169.html",
    "11142308.html",
    "7808330.html",
    "23904746.html",
    "8845555.html",
    "26222394.html",
    "17205837.html",
    "23919305.html",
    "8914821.html",
    "18085932.html",
    "17201239.html",
    "20770172.html",
    "14084331.html",
    "16325288.html",
    "23435803.html",
    "21950252.html",
    "15745076.html",
    "8757963.html",
    "20879582.html",
    "5842852.html",
    "15838346.html",
    "8626318.html",
    "13174616.html",
    "28112410.html",
    "22057531.html",
    "10717047.html",
    "18447133.html",
    "11572046.html",
    "21570997.html",
    "14820638.html",
    "7476661.html",
    "18985115.html",
    "8026706.html",
    "17750761.html",
    "18474041.html",
    "27877076.html",
    "6672657.html",
    "16925890.html",
    "9286391.html",
    "16437165.html",
    "7415966.html",
    "26456590.html",
    "11135800.html",
    "24013599.html",
    "21077159.html",
    "26898465.html",
    "19565584.html",
    "12722158.html",
    "15526985.html",
    "10491974.html",
    "9416089.html",
    "6693064.html",
    "8195783.html",
    "18430388.html",
    "17541220.html",
    "20796307.html",
    "22716211.html",
    "19029309.html",
    "4992182.html",
    "10518563.html",
    "28884361.html",
    "13432616.html",
    "23487701.html",
    "9052706.html",
    "27928767.html",
    "18661600.html",
    "29599616.html",
    "19682600.html",
    "28822848.html",
    "24428472.html",
    "9827417.html",
    "21207569.html",
    "5932179.html",
    "6723942.html",
    "23648777.html",
    "7809409.html",
    "29493217.html",
    "18792732.html",
    "28032695.html",
    "23748579.html",
    "13729379.html",
    "6683858.html",
    "27626019.html",
    "6731233.html",
    "26789463.html",
    "5179454.html",
    "5646016.html",
    "23218237.html",
    "15887688.html",
    "16910398.html",
    "25555606.html",
    "5932336.html",
    "11849467.html",
    "18650799.html",
    "9836651.html",
    "26609955.html",
    "8683748.html",
    "16637849.html",
    "24038948.html",
    "11391412.html",
    "10724014.html",
    "10617058.html",
    "8567072.html",
    "23339270.html",
    "23464878.html",
    "12717109.html",
    "16428956.html",
    "29739601.html",
    "26643525.html",
    "14967891.html",
    "28756671.html",
    "27773817.html",
    "9635520.html",
    "5546848.html",
    "26369409.html",
    "18613671.html",
    "16023253.html",
    "27475948.html",
    "10800831.html",
    "4805214.html",
    "21218995.html",
    "23596557.html",
    "28761969.html",
    "13562949.html",
    "28342704.html",
    "27868648.html",
    "25204028.html",
    "5914968.html",
    "24074255.html",
    "7910925.html",
    "10188862.html",
    "17302123.html",
    "11653353.html",
    "8122937.html",
    "13715208.html",
    "8117333.html",
    "5610046.html",
    "14449126.html",
    "24034108.html",
    "26351690.html",
    "11017799.html",
    "9163107.html",
    "10153802.html",
    "23203475.html",
    "24005884.html",
    "25531377.html",
    "9332906.html",
    "7045114.html",
    "8815989.html",
    "9531456.html",
    "18569099.html",
    "18442895.html",
    "9786851.html",
    "23438311.html",
    "27670235.html",
    "14648413.html",
    "7188238.html",
    "29215894.html",
    "27641724.html",
    "19926126.html",
    "13310453.html",
    "29808480.html",
    "10767592.html",
    "18135311.html",
    "11929716.html",
    "7134872.html",
    "5042165.html",
    "24578062.html",
    "25631032.html",
    "25051964.html",
    "23424126.html",
    "11204106.html",
    "14246898.html",
    "20336520.html",
    "11930753.html",
    "21727431.html",
    "16982099.html",
    "28977098.html",
    "19559842.html",
    "25123808.html",
    "23684612.html",
    "9719951.html",
    "14009885.html",
    "22208536.html",
    "26579500.html",
    "6342345.html",
    "27177152.html",
    "9051006.html",
    "7213007.html",
    "7957255.html",
    "25574765.html",
    "6224775.html",
    "20693983.html",
    "21943161.html",
    "15665044.html",
    "24986111.html",
    "6806952.html",
    "23487481.html",
    "5694838.html",
    "19585864.html",
    "28455286.html",
    "26684121.html",
    "21484880.html",
    "13547296.html",
    "16926801.html",
    "26375372.html",
    "22325696.html",
    "25840893.html",
    "18917427.html",
    "15211465.html",
    "28346785.html",
    "21662510.html",
    "21288442.html",
    "20956609.html",
    "14696582.html",
    "20635982.html",
]

for file in files:
    os.system(f"mv ./dataset/darkweb/{file} ./dataset/notsuredrugs/{file}")