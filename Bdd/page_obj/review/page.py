from Bdd.page_obj.plan.acquisition import Acquisition
from Bdd.page_obj.plan.all_parameters import AllParametersView
from Bdd.page_obj.plan.view import View
from Bdd.page_obj.review.image_parameters import ImageParameters
from autowork_core.page import WindowPage


class ReviewPage(WindowPage):
    root_locator_file = "review/window.yaml"
    root_locator = "SpectralViewer_window"

    @property
    def image_parameters(self) -> ImageParameters:
        return self.get_view(ImageParameters)

