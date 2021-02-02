
import analysis_black_jack as bj

def test_setup():
    a = bj.MakeBlackJack()
    (b,c,d) = a.setup()
    print(b, c, d)
