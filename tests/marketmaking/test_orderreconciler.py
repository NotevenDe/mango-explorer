import mango

from decimal import Decimal

from mango.marketmaking.orderreconciler import NullOrderReconciler

from ..fakes import fake_model_state


def test_nulloperation() -> None:
    existing = [
        mango.Order.from_basic_info(mango.Side.BUY, price=Decimal(1), quantity=Decimal(10)),
        mango.Order.from_basic_info(mango.Side.SELL, price=Decimal(2), quantity=Decimal(20))
    ]
    desired = [
        mango.Order.from_basic_info(mango.Side.BUY, price=Decimal(3), quantity=Decimal(30)),
        mango.Order.from_basic_info(mango.Side.SELL, price=Decimal(4), quantity=Decimal(40))
    ]

    model_state = fake_model_state()
    actual = NullOrderReconciler()
    result = actual.reconcile(model_state, existing, desired)

    assert result.to_keep == existing
    assert result.to_ignore == desired
