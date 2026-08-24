from autowork_core.page import WindowView


class Preferences(WindowView):
    locator_file = "patient_directory/preferences.yaml"
    # active_locator = "$title_vertical_scroll_bar"
    active_locator = None

    def scroll_the_title_bar(self):
        self.scroll_to(target='$title_vertical_scroll_bar',steps=2)

    def open_licensing(self):
        self.click('$licensing_button')

    def scroll_the_license_list(self):
        self.scroll_to(target='$license_list_scroll_bar', steps=5)
        self.scroll_to(target='$license_list_scroll_bar', steps=5)
        self.scroll_to(target='$license_list_scroll_bar', steps=5)
        self.scroll_to(target='$license_list_scroll_bar', steps=5)
        self.scroll_to(target='$license_list_scroll_bar', steps=5)
        self.scroll_to(target='$license_list_scroll_bar', steps=5)

    def Absolute_Delay_license_type_is_None(self):
        self.assert_attr_equal('$Absolute_Delay_license_type','Value.Value',None)

    def Absolute_Delay_license_type_is_Permanent(self):
        self.assert_attr_equal('$Absolute_Delay_license_type','Value.Value','Permanent')

    def Precise_Phase_license_type_is_None(self):
        self.assert_attr_equal('$Precise_Phase_license_type','Value.Value',None)

    def Precise_Phase_license_type_is_Permanent(self):
        self.assert_attr_equal('$Precise_Phase_license_type','Value.Value','Permanent')