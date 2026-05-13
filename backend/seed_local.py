"""本地开发数据填充脚本（SQLite）"""
import asyncio
import uuid
from datetime import date

import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models import Base, User, Shop, ShopPhoto

DB_URL = "sqlite+aiosqlite:///./sakura_dev.db"

engine = create_async_engine(DB_URL, connect_args={"check_same_thread": False})
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


SHOPS_DATA = [
    dict(name="一兰拉面", prefecture="福冈县", city="博多区", category="餐飲", tag="拉麵",
         visit_date=date(2026, 2, 14), rating=4.8, featured=True,
         one_liner="独自一人的隔断座位，一碗纯粹的博多豚骨，世界安静了。",
         description="一蘭的独立隔间设计让人完全专注于碗中的汤头，与外界隔绝的片刻反而成了旅途中难得的独处时光。豚骨汤底浓而不腻，面条硬度可自选，配上秘制红辛酱，层次丰富。",
         cover_image="https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&q=80",
         lat=33.5898, lng=130.4197, phone="0120-29-2929", hours="24小時營業",
         photos=["https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=800&q=80",
                 "https://images.unsplash.com/photo-1617196034183-421b4040ed20?w=800&q=80",
                 "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&q=80"]),
    dict(name="猿田彦珈琲", prefecture="东京都", city="涩谷区", category="餐飲", tag="咖啡",
         visit_date=date(2026, 1, 28), rating=4.5, featured=True,
         one_liner="表参道小巷里的金色招牌，一杯手冲让清晨慢下来。",
         description="隐于表参道背街的精品咖啡馆，光线透过落地窗洒进来，咖啡师专注的样子本身就是一道风景。单品手冲香气细腻，轻食搭配也很用心，适合独处或小声聊天的午后。",
         cover_image="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80",
         lat=35.6647, lng=139.7074, phone="03-6450-6530", hours="08:00–22:00",
         photos=["https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80",
                 "https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800&q=80"]),
    dict(name="京都一之傳", prefecture="京都府", city="中京区", category="餐飲", tag="和食",
         visit_date=date(2026, 1, 15), rating=4.9, featured=True,
         one_liner="西京味噌腌制的银鳕鱼，入口即化，京都的冬天因此有了温度。",
         description="创业超过百年的西京漬け名店，午市定食性价比极高。座位面向枯山水小庭，食物与空间都精致克制。银鳕鱼腌渍三天，烤制时表皮微焦，内里嫩滑。",
         cover_image="https://images.unsplash.com/photo-1547592180-85f173990554?w=800&q=80",
         lat=35.0042, lng=135.7592, phone="075-221-0003", hours="11:30–14:00 / 17:00–21:00（週一休）",
         photos=["https://images.unsplash.com/photo-1547592180-85f173990554?w=800&q=80",
                 "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&q=80",
                 "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800&q=80"]),
    dict(name="道顿堀今井", prefecture="大阪府", city="中央区", category="餐飲", tag="烏冬",
         visit_date=date(2025, 12, 30), rating=4.6, featured=False,
         one_liner="大阪最老牌的乌冬，汤底清澈见底，却鲜得让人无言。",
         description='道顿堀的喧嚣外，今井的店内始终保持着一种老派的从容。昆布与鲣鱼的出汁在这里得到了最诚实的诠释，清汤乌冬看似简单，喝下第一口才明白何谓"大阪风味"。',
         cover_image="https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=800&q=80",
         lat=34.6685, lng=135.5020, phone="06-6211-0319", hours="11:00–21:30（週三休）",
         photos=["https://images.unsplash.com/photo-1557872943-16a5ac26437e?w=800&q=80",
                 "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&q=80"]),
    dict(name="中洲屋台", prefecture="福冈县", city="博多区", category="餐飲", tag="居酒屋",
         visit_date=date(2025, 12, 20), rating=4.4, featured=True,
         one_liner="那珂川边的屋台，喝一杯生啤，夜风带着博多的人情味。",
         description="福冈屋台文化的精髓不在食物本身，而在那种与陌生人肩并肩坐下、天南海北聊开的随意与温暖。半露天的摊位，炉火的暖意，酒杯碰撞的声音，构成了博多夜晚最真实的底色。",
         cover_image="https://images.unsplash.com/photo-1580442151529-343f2f6e0e27?w=800&q=80",
         lat=33.5926, lng=130.4048, hours="18:00–01:00（週日休）",
         photos=["https://images.unsplash.com/photo-1580442151529-343f2f6e0e27?w=800&q=80",
                 "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80"]),
    dict(name="新宿思い出横丁", prefecture="东京都", city="新宿区", category="餐飲", tag="燒鳥",
         visit_date=date(2025, 11, 8), rating=4.3, featured=False,
         one_liner="昭和气息扑面而来，烤鸡串的烟雾与霓虹灯混在一起，穿越感十足。",
         description="战后重建的小巷原貌至今未变，每一间烧鸟小店都像是时间胶囊，现代东京最珍贵的缝隙之一。烟雾、喧闹、拥挤，但每一口烤串都坦率得令人感动。",
         cover_image="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80",
         lat=35.6939, lng=139.7004, hours="各攤位不同，約 17:00–24:00",
         photos=["https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80",
                 "https://images.unsplash.com/photo-1580442151529-343f2f6e0e27?w=800&q=80"]),
    dict(name="筑地场外 寿司大", prefecture="东京都", city="中央区", category="餐飲", tag="壽司",
         visit_date=date(2025, 10, 25), rating=5.0, featured=True,
         one_liner="清晨五点排队，握寿司一个接一个，每口都是海洋的心意。",
         description="为了这顿早饭等了两个小时，吃完之后觉得一切都值得。鱼货新鲜到几乎不需要酱油，这才是东京的寿司应有的样子。师傅握寿司的节奏沉稳，每一个都是刚好的温度和力道。",
         cover_image="https://images.unsplash.com/photo-1617196034183-421b4040ed20?w=800&q=80",
         lat=35.6654, lng=139.7707, phone="03-3541-6006", hours="05:00–14:00（週三・日休）",
         photos=["https://images.unsplash.com/photo-1617196034183-421b4040ed20?w=800&q=80",
                 "https://images.unsplash.com/photo-1510130387-6f748462204a?w=800&q=80",
                 "https://images.unsplash.com/photo-1547592180-85f173990554?w=800&q=80"]),
    dict(name="京都锦市场", prefecture="京都府", city="中京区", category="購物", tag="市場",
         visit_date=date(2025, 10, 10), rating=4.2, featured=False,
         one_liner="京都的厨房，百年老街里每一摊都是惊喜。",
         description="京都的厨房——锦市场里藏着无数惊喜，现做麻薯热乎乎刚出炉，撒上黄豆粉和黑蜜，是最朴素的幸福。站在市场里边走边吃，这才是京都该有的节奏。",
         cover_image="https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&q=80",
         lat=35.0044, lng=135.7657, hours="10:00–18:00",
         photos=["https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&q=80",
                 "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800&q=80"]),
    dict(name="大阪黑门市场", prefecture="大阪府", city="中央区", category="購物", tag="海鮮",
         visit_date=date(2025, 9, 18), rating=4.5, featured=False,
         one_liner="大阪的厨房，市场里站着吃的海鲜定食，新鲜、粗犷、满足。",
         description="大阪的厨房——黑门市场的活力让人振奋，松叶的定食不讲究摆盘，只讲究食材本身的说话权。刚切的生鱼片、现烤的贝壳，配上一碗白米饭，粗粝却真实。",
         cover_image="https://images.unsplash.com/photo-1510130387-6f748462204a?w=800&q=80",
         lat=34.6708, lng=135.5063, hours="09:00–18:00（週三休）",
         photos=["https://images.unsplash.com/photo-1510130387-6f748462204a?w=800&q=80",
                 "https://images.unsplash.com/photo-1617196034183-421b4040ed20?w=800&q=80"]),
    dict(name="镰仓 茶房 雪乃下", prefecture="神奈川县", city="镰仓市", category="餐飲", tag="甜點",
         visit_date=date(2025, 8, 30), rating=4.7, featured=True,
         one_liner="镰仓老街的刨冰，草莓炼乳堆得像雪山，夏日的高配答案。",
         description="雪乃下的刨冰质地极细腻，几乎是蓬松的，配上自制草莓酱，在小町通的人潮中找到一席静谧的角落，时间仿佛停住。排队值得，坐下来的那一刻是真实的夏日奖励。",
         cover_image="https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800&q=80",
         lat=35.3197, lng=139.5502, phone="0467-61-3543", hours="10:00–17:30（週四休）",
         photos=["https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800&q=80",
                 "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&q=80",
                 "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80"]),
]


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with Session() as db:
        # 用户
        hashed = bcrypt.hashpw("56501109".encode(), bcrypt.gensalt()).decode()
        user = User(id=uuid.uuid4(), username="kudo1109", hashed_password=hashed)
        db.add(user)
        await db.flush()

        # 店铺（system default，user_id=None）
        for d in SHOPS_DATA:
            photos = d.pop("photos", [])
            shop = Shop(id=uuid.uuid4(), user_id=None, **d)
            db.add(shop)
            await db.flush()
            for i, url in enumerate(photos):
                db.add(ShopPhoto(id=uuid.uuid4(), shop_id=shop.id, url=url, sort_order=i))

        await db.commit()
        print(f"✓ 插入用户 kudo1109 + {len(SHOPS_DATA)} 间店铺")


asyncio.run(main())
