from frontend.views.Registration import Registration
class Endpointregistration(Registration): #inherits the registration class
    def __init__(self, master, reg_type):
        super().__init__(master,reg_type)
        self.master.title("ZeroDown: Endpoint Registration")

        