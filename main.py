import discord
from discord.ext import commands

class PeiwanBot:
    def __init__(self):
        self.total_income = 0  # 累计总收入
        self.orders = []  # 订单列表
        self.completed_orders = []  # 已结单
        self.pending_orders = []  # 未结单
        self.categories = {}  # 多品类及抽成比例
        self.user_balances = {}  # 用户充值、赠送、消费数据

    def add_order(self, user, category, amount, price_per_unit, status="pending"):
        """自动报单"""
        commission_rate = self.categories.get(category, 0)  # 获取抽成比例
        net_income = amount * price_per_unit * (1 - commission_rate)  # 计算净收入
        order = {
            "user": user,
            "category": category,
            "amount": amount,
            "price_per_unit": price_per_unit,
            "net_income": net_income,
            "status": status
        }
        self.orders.append(order)
        if status == "completed":
            self.completed_orders.append(order)
            self.total_income += net_income
        else:
            self.pending_orders.append(order)
        return order

    def complete_order(self, order):
        """结单并统计收入"""
        if order in self.pending_orders:
            self.pending_orders.remove(order)
            self.completed_orders.append(order)
            order["status"] = "completed"
            self.total_income += order["net_income"]

    def set_category(self, category, commission_rate):
        """设置品类及抽成比例"""
        self.categories[category] = commission_rate

    def get_summary(self):
        """获取订单汇总"""
        return {
            "total_income": self.total_income,
            "completed_orders": len(self.completed_orders),
            "pending_orders": len(self.pending_orders)
        }
    
    def recharge(self, user, amount):
        """累计充值"""
        if user not in self.user_balances:
            self.user_balances[user] = {"recharge": 0, "gift": 0, "spend": 0, "balance": 0}
        self.user_balances[user]["recharge"] += amount
        self.user_balances[user]["balance"] += amount

    def gift(self, user, amount):
        """累计赠送"""
        if user not in self.user_balances:
            self.user_balances[user] = {"recharge": 0, "gift": 0, "spend": 0, "balance": 0}
        self.user_balances[user]["gift"] += amount
        self.user_balances[user]["balance"] += amount
    
    def spend(self, user, amount):
        """累计消费"""
        if user in self.user_balances and self.user_balances[user]["balance"] >= amount:
            self.user_balances[user]["spend"] += amount
            self.user_balances[user]["balance"] -= amount

    def get_user_balance(self, user):
        """查询用户累计数据"""
        return self.user_balances.get(user, {"recharge": 0, "gift": 0, "spend": 0, "balance": 0})

# Discord Bot 设置
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
pw_bot = PeiwanBot()

@bot.event
async def on_ready():
    print(f'已登录为 {bot.user}')

@bot.command()
async def add_order(ctx, user: str, category: str, amount: int, price: int):
    order = pw_bot.add_order(user, category, amount, price)
    await ctx.send(f'订单已创建: {order}')

@bot.command()
async def complete_order(ctx, user: str):
    for order in pw_bot.pending_orders:
        if order["user"] == user:
            pw_bot.complete_order(order)
            await ctx.send(f'订单已完成: {order}')
            return
    await ctx.send('未找到该用户的待处理订单')

@bot.command()
async def summary(ctx):
    summary = pw_bot.get_summary()
    await ctx.send(f'订单汇总: {summary}')

@bot.command()
async def balance(ctx, user: str):
    balance_info = pw_bot.get_user_balance(user)
    await ctx.send(f'{user} 余额信息: {balance_info}')

# 运行Bot（需要填写你的Token）
TOKEN = "你的Discord Bot Token"
bot.run(TOKEN)
