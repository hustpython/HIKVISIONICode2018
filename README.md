
#### 1、赛题
复赛题目



背景介绍

海康机器人行业级无人机业务依托海康威视视频技术的积累，进行跨技术领域的深度整合，以视频图像处理为核心、以产品安全为基石、以智能应用为导向、以满足行业需求为目标，自主研发了雄鹰系列无人机及保障低空空域安全的无人机干扰器，以丰富的产品为客户提供有针对性的行业解决方案，立足安防，专注行业。题目以无人机为主题，考察参赛队伍的综合能力。这个夏天，来一起AI对战吧！

复赛无人机说明

由于目前技术的限制，无人机的飞行过程中耗电量极大。为了方便做题，现在假设无人机空载的时候，耗电量极低，可以忽略不计。载货时，耗电量跟货物的重量成正比，比例系数为1，例如货物重量为100，那么单位时间的耗电量为100个单位电能。单位时间耗电量跟无人机有没有移动无关，即静止状态也需要耗能，包括无人机在地面的时候（停机坪除外）。不同的无人机电池容量不同。如果无人机在外面飞行过程中出现没电量（空载除外），即视为无人机坠毁（不论是否在地面）。选手可以在自己的停机坪对无人机进行充电，单位时间充的电量跟无人机机型有关。（无人机只能在空载的时候进行充电，如果载有货物，不能进行充电，否则视为犯规）。停机坪可以同时对多架无人机进行充电（充满电后，可以停留在停机坪）。初始无人机电量都为0，（包括比赛开始时，以及新购买的无人机），因此一开始需要充电（不打算运送货物除外）。

#### 2、实战录像
![](./images/vs.gif)
![](./images/vs2.gif)
![](./images/vs3.png)

#### 3、参赛有感
对海康威视的了解，有三次机缘。第一次是在看CCTV4《远方的家》纪录片中有介绍海康在国外的部署，第二次是随室友一起去他本科学校的时候和他在海康的同学在青岛玩了几天，期间有关注过。第三次，就是这次参加海康算法大赛了。之所以要想写关于这次海康的比赛经历，一来是因为自己在算法比赛方面，确实没什么经历，不像那些科班出身的大佬，已经身经百战，习以为常。所以对于自己，就拿这个参加这个比赛本身来说，都是一种值得回味的新体验。二来，整个期间确实经历了一些对自己有意义，有感触的事情，希望能成为自己继续前进的基石。  
       了解到这次比赛是在大活的一个实习宣讲会中，当时去的人很少，之所以去这个宣讲会，一来是基于前两次的了解，二来想具体了解一下这个算法比赛，三则抱着能抽个奖啥的心态。和之前的华为相比感觉这个就像是来凑热闹的。结果呢，和百度百科差不多的介绍，算法比赛内容没怎么细讲，抢答抽奖自然没有啥结果。

  

       回去之后，看了一下官网比赛题目，看不懂呢，和AI有什么关系呢这个。大概是要控制无人机取货？还要考虑周围建筑，雾区，飞行高度，还能购买无人机，无人机碰撞……反正当时没看懂，而且还要连接他的服务器在线获取数据…..总而言之，没看懂，也觉得这个门槛对于自己来说…太高了，很复杂，但也很好玩不是。距离他们服务器提供调试数据还有几天，然后就没管。到了他们那边开始可以调试了，赶紧报了个名，准备写代码，把官网的赛题介绍又看了五六遍，才大概明白了其中主旨大意。当时在学C++,就打算先用cpp写个玩玩。具体过程就不必细说了。cpp虽然可以写,但是很多高级函数不会用，只能写一些结构体，然后用各种vector和for循环了。眼看，截止日期不远了，就赶紧换Python了，原因自不用说，关键时刻还是怎么简单怎么来，能直接用的绝不自己去造轮子。

       初赛截止时，差不多有900支队伍提交了代码。根据前几次的分组测评结果，应该处于中上水平。初赛淘汰比例不是很大。所以也没什么压力，如果进不了也还好，就不用继续下去了。这几天想这些逻辑，头已经很大了，感觉每天一睡醒来满眼都是无人机乱飞。在提交截止前一天，把室友也加入了队伍。如果能进入复赛，也能有个帮手不用孤军奋战。

       一共有80支队伍进入了复赛，我也幸运地加了其中。复赛在初赛的基础上加了一个电量限制的条件，时间一共五天半。我在复赛开始的第一天，把这个逻辑实现了，尽量不要出现规则上的错误和自己的飞机相撞的情况。这个得不断调试，各种莫名其妙的错误总会层出不穷。但是第二天测评的时候还是有一些小错误，继续修改，反正前两天的时间都要来实现保证代码能够满足新加的条件。

       终于，在第三天的测评中，榜上有名了。这里解释一下他们的游戏规则，为了方便参赛队伍调试，他们会每天固定时间段对所有队伍就行分组测评，每个组里面的队伍，两两对战，互换位置。然后根据每场比赛结果，来获得相应的比分。比如，你和其他24个队伍分别进行对抗，如果其中有20场你都胜利了，那么你的成绩就是20。这个成绩只能算是一定的参考，不能算着绝对成绩，因为有可能你这次所在的组的队伍的总体成绩都很一般，就算你全部赢了，也可能        没有另一组全是大佬的最后一名厉害。大概就是这个意思，如果全部都要对战的话，这个场次就过多了，而且只是测评，所有没有这个必要。测评完毕可以通过查看比赛的录像，查找自己的算法上面的bug。

      下午，和组队的室友一起讨论接下来该怎么办，因为目前的状况来看，逻辑上虽然没什么问题了，但是购买的飞机一直很少，因为没有运送货物赚钱。我当时就想着，在和他们官网的随机游荡机器人对战时（官网提供的调试机器人），如果拿不到20000的价值量，那根本就没法搞了。事实确实如此，因为最后的对战就是靠购买的飞机数量的优势，来压倒对方，以一换一，就看最后谁先把对方的无人机撞完。

在初赛中，用了一个贪心算法，导致很多无人机没有取到适合他的载重量和价值的货物。但是那时候大家似乎都还很单纯，不会无缘无故把无人机开过来撞你。进入复赛之后，各种奇葩战略都出来了，有用自己价值比较小的撞别人价值高的无人机的，有用购买的无人机停在别人停机坪上方的，有在别人送货目的地上方拦截的。。。雅然，曾经的一片繁荣的‘贸易’场，已经变成了硝烟弥漫的战场。

       考虑到如何让每一个飞机都能取到适合自己的货物。飞机选择它认为最好的货物，那个货物也应该选择它认为最适合来运送它的飞机，如果这双方都能一致，这就完成了一次配对，我想实现这样的功能。

         在网上搜索，关键词用是配对算法，检索到的是，男女配对算法，其实大体思路差不多，最终能够让每一个男生都能从名单中找到一个适合他的另一半，女生也能找到他的白马王子。他们的代码我没看，也没时间看了。有想法就应该赶紧行动了。

我承认我不是一个写代码效率很高的人，也许是天生的的拙笨，好在我还能坚持，我只要能一步步靠近，就不那么轻易放弃。当天睡觉之前把这个功能写完了。测试结果，总价值能够达到18000左右，和之前的算法的9000相比，已经翻倍了，而且距离两万已经很近了。

        第四天的早晨，如约而至。室友说他要调整一下关于那个配对取货的代码。我继续修改一些新出现的问题，比如自己飞机误撞，撞击敌机时容易跟丢…。经过室友的调试，和电脑机器人的对战中，总价值很快超过2万。我一上午只改了一个bug。快到的中午的时候赶紧把代码提交了，然后想查看一下测评结果。中午测评结果出来了，很失望，没有进入排行榜。他的排行榜只显示每组成绩超过10分的队伍，什么鬼，写了这么多怎么还退步了呢，越想越感觉哪里不对劲，是不是因为测评的不是之前的代码，因为上面的时间确实不是中午11点提交的，但是看了视频对战的路线确实是修改之后的。所以，最终结果应该是这样，要么我们没有提交最新代码，我们也无法知道我们新的代码的实战效果如何，要么测评的就是修改后的代码而且测评结果表明，我们的实战效果确实不尽人意。这两个结果都不是我想要的，因为测评只有一次机会了，晴天霹雳。下午室友继续优化取货，我也没时间苦恼了，因为还有很多功能没实现。我也赶紧把撞击拦截敌机以及占领对方停机坪的策略写一下，还有充电，购买飞机…

 

       第五天，最后一天了，也是最后一次测评了，我也赶紧把取货的策略改成最新优化过的，然后不断调试争取在中午之前再改一些bug。上午的时间真的有些短暂，短暂的让你都不敢写一些新的功能。提交完代码，和室友吃饭说，如果这次进不了排行榜，那就放弃吧。中午吃饭的时候，成绩就出来了，还好，努力没有白费，18分，这个数字虽然不能决定什么，却足以能够支持我们再剩下不多的时间内继续多写几行代码，多想一些策略，多和别人对战几次，多找几个bug，多一些幻想……幻想着，拿着公司的报销费去杭州，这应该比自己掏钱要爽的多。

中午，本想睡一会，但是哪里睡得着呢，明天就停止提交了，命悬一线的感觉。在床上辗转反侧了几次就下来了，看了一些中午的测评录像，确实还有很多问题。下午继续调试，室友用了   自己写的购买飞机的策略，已经能够和电脑的对战中拿到三万，如果只考虑无人机送货，这个成绩绝对已经接近货物价值极限了，但是这个毕竟是几乎最理想的情况下了，没有任何阻挠，最后的最后我也没有将他的这个购机策略加进来，因为我感觉问题的关键不在于此，开局几分钟就决定了胜负。

        我晚上继续修改一些bug，找一些队伍来私下约战，此刻大家都很强大，改完代码就找人约战，想从测评中战胜自己的队伍中寻找突破。如果在对战过程中发现问题，就会和对方说，我这有一个bug，我去改代码，有时间再战。如果干倒了对方，就会继续找人对战或者隐匿起来。尝试新策略，修改代码已经成了最后时刻的主旋律。若你持着自己在测评中的成绩，半天不改代码，肯定会有一大批人追上来。我就亲眼目睹一些在初赛排名很高的人渐渐排到了尾部，也有很厉害的后来居上。当然我们还会关注那些不离前三的队伍，真的超级厉害，他们就像标准答案一般供我们膜拜。

下午的对战情况，不是很乐观，总体输的比较多，有发现问题之所在：虽然我们的策略保证了我们能够整体比较优地取到货物，但是由于货物发布的随机性，很有可能会绕的很远去取到价值很高的货物，一旦别人利用距离带来的时间优势领先过多，后面就无法弥补了会一直被别人压着。但是对有些队伍我的这一套策略对他们很致命。所以关于取货没有怎么大改动。

        我当时所能做的就是继续强壮逻辑，调整一些参数，尽量避免不必要的策略失误…这些所谓的失误都是自己在和别人的对战中观察到的一些没有按照自己逾期执行的bug。现在想来，这个最后功能的实现，是自己最开始从想当然的逻辑出发，实现主要功能，比如起飞，取货，充电，撞击。然后再去细细考虑，比如如何选货，什么时候去充电，遇到雾中的飞机怎么办。最后就是通过观察比赛中的每一架飞机在地图中的移动，取货，撞击…才会发现其中还有很多工作没有做好…。

        为了方便大家多一些调试机会，官方于凌晨0点又增加了一次测评，一个小时就出成绩了，虽然数值不是很低，20分，组内排名也靠前。但是大略看了一下其中的队伍，都是自己不认识的，或者是自己感觉不怎么厉害的队伍。对于这20分，自然无法成为使自己安然的良药，但是也不能成为让自己继续修改的动力了，最终代码定格在746行。

       第二天早起之后就再也没有想无人机比赛的事情，就那么漠然地等待着时间流过中午12点，然后把结果交给未知的一切。

       直到今天，此时此刻，知道自己没有进入前15名，没有成为决赛队伍中的一员，我在这 千军万马过多木桥 的征程中，没能到达彼岸。顿时万分惭愧，真后悔自己 在最后一刻就那么放弃了，就那么让自己假装安然了，就那么欣然接受命运的安排。
