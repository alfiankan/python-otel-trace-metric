import time
from datetime import datetime

from otel import init_otel, to_span, create_metrcis_meter_counter
from opentelemetry.trace.status import StatusCode
from opentelemetry.trace import Tracer
from opentelemetry.metrics import Counter
from opentelemetry.sdk.metrics import Meter


class ApplicationContext:
    tracer: Tracer
    meter: Meter
    metrics: dict[str, Counter]


def buat_event_penggandaan_uang(ctx: ApplicationContext) -> None:
    with ctx.tracer.start_as_current_span(name="menggandakan uang event push") as span:
        print("seseorang menggandakan uang")
        if int(datetime.now().second) % 2 != 0:
            # simulasi error
            print("error simulated")
            to_span(span).record_exception(Exception("Message brokernya mati"))
            to_span(span).set_status(StatusCode.ERROR)


def gandakan_uang(ctx: ApplicationContext, saldo: int) -> int:
    counter: Counter = ctx.metrics['user_menggandakan_uang']

    with ctx.tracer.start_as_current_span(name="menggandakan uang") as span:
        ganda = saldo * 2
        to_span(span).set_attributes({"saldo_awal": saldo, "saldo_akhir": ganda})
        buat_event_penggandaan_uang(ctx)
        counter.add(1)


def tambahuang(ctx: ApplicationContext, saldo: int) -> bool:
    with ctx.tracer.start_as_current_span(name="menambah saldo") as span:
        to_span(span).set_attribute("saldo", saldo)
        if int(datetime.now().second) % 2 != 0:
            # simulasi error
            print("error simulated")
            to_span(span).record_exception(Exception("Ada error dicatat dimasukan ke trace"))
            to_span(span).set_status(StatusCode.ERROR)
            return False

        to_span(span).set_status(StatusCode.OK)
        return True


def delivery(ctx: ApplicationContext, user_id: str):
    """
    ini adalah fungsi yang paling awal
    lalu akan memanggil 2 fungsi lain
    :param user_id:
    :param ctx:
    :return:
    """

    with ctx.tracer.start_as_current_span(name="entrypoint-endpoint-user") as span:
        to_span(span).set_attribute("incoming user id", user_id)

        tambahuang(ctx, 10_000_000)
        gandakan_uang(ctx, 10_000_000)


# init application

# init tracing
tracer = init_otel("uang_service")
ctx = ApplicationContext()
ctx.tracer = tracer
ctx.meter = create_metrcis_meter_counter()
ctx.metrics = dict()
ctx.metrics['akses_aplikasi'] = ctx.meter.create_counter("akses_aplikasi")
ctx.metrics['user_menggandakan_uang'] = ctx.meter.create_counter("user_menggandakan_uang")

while True:
    if datetime.now().second % 2 == 0:
        time.sleep(0.2)
    else:
        time.sleep(0.7)
    print(datetime.now())
    delivery(ctx, user_id="000-LUCY-555-LOCKWOOD")

    counter: Counter = ctx.metrics['akses_aplikasi']
    counter.add(1)
