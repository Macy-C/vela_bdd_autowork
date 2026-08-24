from time import sleep
from autowork_core.page import BasePage


class NotePad(BasePage):

    def test_click(self):
        self.set_root({'class_name':'Notepad',"backend":'uia'},'Notepad_window')
        self.double_click("//MenuItem[@name='文件']")
        self.send_text_keys("root=Notepad_window|//Document[@name='文本编辑器']",'1234567879')
        self.clear_text("root=Notepad_window|//Document[@name='文本编辑器']")
        self.click("root=Notepad_window|ocr=文件")
        # self.wait_pic_present("root=Notepad_window|111")
        # self.click("root=Notepad_window|ocr=11233aasdqwe")
        # self.scroll_to("//Edit[@class_name='Edit'][@control_type='Edit']",steps=2)
        # self.scroll_to("//Document[@class_name='RichEditD2DPT']")
        # self.scroll_to("//Document[@class_name='RichEditD2DPT']")
        # self.scroll_to("//Document[@class_name='RichEditD2DPT']",direction='up',steps=5)
        sleep(3)

