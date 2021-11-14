# # ⚠ Warning
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# [🥭 Mango Markets](https://mango.markets/) support is available at:
#   [Docs](https://docs.mango.markets/)
#   [Discord](https://discord.gg/67jySBhxrg)
#   [Twitter](https://twitter.com/mangomarkets)
#   [Github](https://github.com/blockworks-foundation)
#   [Email](mailto:hello@blockworks.foundation)
from decimal import Decimal

import mango

from .hedger import Hedger
from .ftx import FtxClient
import typing

# # 🥭 Hedger class
#
# A base hedger class to allow hedging across markets.
#

FTX_KEY = ""
FTX_SECRET = ""
SUB_ACCOUNT = "mango-hedge"

class FtxHedger(Hedger):
    def __init__(self, group: mango.Group, underlying_market: mango.PerpMarket) -> None:
        super().__init__()
        self.underlying_market: mango.PerpMarket = underlying_market
        self.market_index: int = group.slot_by_perp_market_address(underlying_market.address).index
        self.ftx = FtxClient(FTX_KEY, FTX_SECRET, SUB_ACCOUNT)
        self.ftx_spot_market = self.underlying_market.base.symbol + "/USD"

    def pulse(self, context: mango.Context, model_state: mango.ModelState) -> None:
        perp_account: typing.Optional[mango.PerpAccount] = model_state.account.perp_accounts_by_index[self.market_index]
        if perp_account is None:
            raise Exception(
                f"Could not find perp account at index {self.market_index} in account {model_state.account.address}.")
        perp_position: mango.InstrumentValue = perp_account.base_token_value
        self.logger.debug(f"perp_position_rounded {perp_position}")
        balances = self.ftx.get_balances()
        spot_balance = None
        for b in balances:
            if b['coin'] == str(self.underlying_market.base.symbol).upper():
                spot_balance = b['total']
        delta = Decimal(spot_balance) + perp_account.base_token_value.value
        if abs(delta) > 0.05:
            order_book = self.ftx.get_orderbook(self.ftx_spot_market)
            side = "buy" if delta < 0 else "sell"
            price = order_book['bids'][0][0] if delta < 0 else order_book['asks'][0][0]
            self.ftx.cancel_orders(self.ftx_spot_market)
            self.ftx.place_order( self.ftx_spot_market, side, price, float(abs(delta)), 'limit',post_only=True)

    def __str__(self) -> str:
        return "« Ftx Hedger »"

    def __repr__(self) -> str:
        return f"{self}"
