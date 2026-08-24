from autowork_core.page import WindowPage

from Bdd.page_obj.exam_card_manager.clinical_sequence import (
    ClinicalSequenceView,
)
from Bdd.page_obj.exam_card_manager.exam_card_selection import (
    ExamCardSelectionView,
)
from Bdd.page_obj.exam_card_manager.scan_parameters import (
    ScanParametersView,
)


class ExamCardManagerPage(WindowPage):
    root_locator_file = "exam_card_manager/window.yaml"
    root_locator = "mainform_window"

    @property
    def exam_card_selection(self) -> ExamCardSelectionView:
        return self.get_view(ExamCardSelectionView)

    @property
    def clinical_sequence(self) -> ClinicalSequenceView:
        return self.get_view(ClinicalSequenceView)

    @property
    def scan_parameters(self) -> ScanParametersView:
        return self.get_view(ScanParametersView)