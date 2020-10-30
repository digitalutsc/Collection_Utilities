/**
 * Changes the variable validation if needed
 */

var ss=SpreadsheetApp.getActiveSpreadsheet();
var activeCell = ss.getActiveCell();

var type = {
    sheet: 'VALIDATION',
    range: 'A2:A'
}

var automaker = {
    sheet: 'VALIDATION',
    range: 'B2:B'
}

var country = {
    sheet: 'VALIDATION',
    range: 'C2:C'
}

/**
 * Creates a menu entry in the Google Docs UI when the document is opened.
 *
 * @param {object} e The event parameter for a simple onOpen trigger. To
 *     determine which authorization mode (ScriptApp.AuthMode) the trigger is
 *     running in, inspect e.authMode.
 */
function onOpen(e) {
    SpreadsheetApp.getUi().createMenu('Sidebar')
        .addItem('Show Sidebar', 'showSidebar')
        .addToUi();
        showSidebar();
}


/**
 * Opens a sidebar in the document containing the add-on's user interface.
 */

function showSidebar() {
    SpreadsheetApp.getUi()
        .showSidebar(HtmlService.createTemplateFromFile('SIDEBAR')
            .evaluate()
            .setSandboxMode(HtmlService.SandboxMode.IFRAME)
            .setTitle('Multiple selector'));
}

function getOptions() {
  if(activeCell.getColumn() == 6 && activeCell.getRow() >= 2 && ss.getActiveSheet().getName()=="Main Sheet") {
    return SpreadsheetApp.getActive().getSheetByName(type.sheet).getRange(type.range).getDisplayValues()
        .filter(String)
        .reduce(function(a, b) {
            return a.concat(b)
        })
  }
  else if(activeCell.getColumn() == 7 && activeCell.getRow() >= 2 && ss.getActiveSheet().getName()=="Main Sheet") {
    return SpreadsheetApp.getActive().getSheetByName(automaker.sheet).getRange(automaker.range).getDisplayValues()
        .filter(String)
        .reduce(function(a, b) {
            return a.concat(b)
        })
  }
  else if(activeCell.getColumn() == 8 && activeCell.getRow() >= 2 && ss.getActiveSheet().getName()=="Main Sheet") {
    return SpreadsheetApp.getActive().getSheetByName(country.sheet).getRange(country.range).getDisplayValues()
        .filter(String)
        .reduce(function(a, b) {
            return a.concat(b)
        })
  }
}

function process(arr) {
    arr.length > 0 ? SpreadsheetApp.getActiveRange().clearContent().setValue(arr.join(", ")) :
        SpreadsheetApp.getUi().alert('No options selected')
}
