from test_bl.test_trassa_plugin.structs_trassa.astdutils import astd_parser


class AstdMsg():
    def __init__(self):
        return



def test_this():
    astd_msg = AstdMsg()
    test_astd = {}

    # ASTD stuct
    test_astd['trassa'] = astd_msg.get_trassa()

    return

if __name__=="__main__":
    test_this()