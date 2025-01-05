from PySide2 import QtWidgets 
import substance_painter.ui 
 
plugin_widgets = [] 
"""Keep track of added ui elements for cleanup""" 
 
def start_plugin(): 
    """This method is called when the plugin is started.""" 
    # Create a simple text widget 
    hello_widget = QtWidgets.QTextEdit() 
    hello_widget.setText("Hello from python scripting!") 
    hello_widget.setReadOnly(True) 
    hello_widget.setWindowTitle("Hello Plugin") 
    # Add this widget as a dock to the interface 
    substance_painter.ui.add_dock_widget(hello_widget) 
    # Store added widget for proper cleanup when stopping the plugin 
    plugin_widgets.append(hello_widget) 
 
def close_plugin(): 
    """This method is called when the plugin is stopped.""" 
    # We need to remove all added widgets from the UI. 
    for widget in plugin_widgets: 
        substance_painter.ui.delete_ui_element(widget) 
    plugin_widgets.clear() 
 
if __name__ == "__main__": 
    start_plugin() 