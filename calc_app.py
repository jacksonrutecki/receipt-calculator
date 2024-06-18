# GUI for the receipt calculator, 09.20.23
# uses the previously developed receipt calculator and incorporates a GUI for ease of use

# NOTE: i really don't love the usage of global variables in this script, but could not seem to find a 
# workaround that wouldn't suck

# GUI will follow the basic format
# - have two buttons for "michael" and "jackson", depending who bought
# - have a button to modify the items of either
#   - when this button is pressed, a textbox displaying the already individual items will pop up, and individual items can be added
# - have a button to add the receipt
#   - when this button is pressed, a blank textbox will pop up where the receipt can be added
# - an "execute" button will be placed at the bottom, where the totals will be returned in the GUI and the Google Sheets file is updated

from receiptcalc2 import *
import tkinter as tk
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# get current date and time

class MainWindow:
    def __init__(self, root, buyers, dir = None):
        if dir:
            # accessing the spreadhseet
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(dir, scope)
            client = gspread.authorize(creds)

            sheet = client.open("Shared Costs 51")
            self.sheet_instance = sheet.get_worksheet(1) # specifies working in the second worksheet (UPDATE WHEN WE MOVE WORKSHEETS)

            self.initUpdateSheetButton()

        # create the main window
        self.mainWindow = root
        self.mainWindow.title("Shared Costs Receipt Calculator")
        self.mainWindow.columnconfigure(1, weight = 1, minsize = 20)
        self.mainWindow.rowconfigure(1, weight = 1, minsize = 50)
        
        # adding buyer buttons to main window
        self.buyer = ""
        self.buyers = buyers
        self.buyerButtons = []
        self.initbuyerButtons(buyers)

        # create parameters for enter receipt window
        self.runningReceipt = ""
        self.initenterReceipt()

        # create parameters for the submit receipt window
        self.res = []
        self.strCosts = ""
        self.initsubmitReceipt()
        
        # output text box
        self.out = tk.Label(text = "")
        self.out.grid(row = 1, column = 2)

    # defines and places all of the buttons relating to the buyer(s)
    def initbuyerButtons(self, buyers):
        # add the label for the buttons
        buyerLabel = tk.Label(text = "Buyer:")
        buyerLabel.grid(row = 0, column = 0)

        # add the buttons
        for i in range(len(buyers)):
            button = tk.Button(text = buyers[i], 
                               command = lambda i = i: self.buyerButtonPressed(self.buyerButtons[i], buyers[i]), 
                               width = 15)
            button.grid(row = i, column = 1)
            self.buyerButtons.append(button)

    # command for what happens when the buyer button is pressed
    def buyerButtonPressed(self, ibutton, buyer):
        for sbutton in self.buyerButtons:
            sbutton.configure(relief = "raised")
        ibutton.configure(relief = "sunken")
        self.buyer = buyer

    # defines and places the "enter receipt button" - stores the items from the receipt in the items field
    def initenterReceipt(self):
        receiptButton = tk.Button(text = "Enter Receipt", command = self.enterReceiptPressed, width = 15)
        receiptButton.grid(row = len(self.buyerButtons), column = 1)

    # update the receipt inside of the main window wiht the result of what is entered in the "enter receipt" box
    def updateReceipt(self, receipt):
        self.runningReceipt = receipt

    # when the "enter receipt" button is pressed, initialize a new class representing the new window
    def enterReceiptPressed(self):
        EnterReceiptWindow(self.runningReceipt, self.updateReceipt)

    def initsubmitReceipt(self):
        submitButton = tk.Button(text = "Submit Receipt", command = self.submitReceiptPressed, width = 15)
        submitButton.grid(row = 0, column = 2)

    def updateRes(self, res):
        self.res = res
        self.updateOut(self.getStrCosts())

    def submitReceiptPressed(self):
        if self.buyer == "":
            self.updateOut("Please select a valid buyer")
        else:
            try:
                self.items = receiptcalc(self.runningReceipt.split("\n"))
                ReceiptSelectWindow(self.items, self.buyers, self.updateRes)
            except IndexError:
                self.updateOut("Please enter a valid receipt")
    
    def updateOut(self, text):
        self.out = tk.Label(text = text)
        self.out.grid(row = 1, column = 2)

    def getStrCosts(self):
        listedItems = self.buyers.copy()
        listedItems.append("Shared")

        self.idhash = {}
        for id in listedItems:
            self.idhash[id] = []

        for i in range(len(self.res)):
            self.idhash[self.res[i]].append(self.items[i])
        
        strout = ""
        for id in listedItems:
            strout += (id + ": $" + str(sum(map(lambda x: float(x.cost), self.idhash[id])))) + "\n"

        return(strout)
    
    def initUpdateSheetButton(self):
        updateSheetButton = tk.Button(text = "Update Sheet", command = self.updateSheetPressed)
        updateSheetButton.grid(row = 2, column = 2)
    
    def updateSheetPressed(self):
        titleRow = "Star Market, " + self.runningReceipt.split("\n")[1]
        numRows = len(self.sheet_instance.get_all_values())

        appendOut = [titleRow]
        indexOfBuyer = self.buyers.index(self.buyer)

        # add the shared cost
        for i in range(len(self.buyers)):
            if i == indexOfBuyer:
                appendOut.append(sum(map(lambda x: x.cost, self.idhash["Shared"])))
            else:
                appendOut.append("")

        # add the individual costs
        for i in range(len(self.buyers)):
            if i == indexOfBuyer:
                runningSum = 0
                runningNotes = ""
                for buyer in self.buyers:
                    if buyer != self.buyer:
                        runningSum += sum(map(lambda x: x.cost, self.idhash[buyer]))
                        runningNotes += "".join(list(map(lambda x: x.formatName(), self.idhash[buyer])))
                appendOut.append(runningSum)
            else:
                appendOut.append("")

        self.sheet_instance.append_row(appendOut)
        self.sheet_instance.insert_notes({
            (chr(ord('@') + indexOfBuyer + 2) + str(numRows + 1)) : "".join(list(map(lambda x: x.formatName(), self.idhash["Shared"]))),
            (chr(ord('@') + indexOfBuyer + 4) + str(numRows + 1)) : runningNotes
        })
    


class EnterReceiptWindow:
    def __init__(self, runningReceipt, updatefunc):
        self.updatefunc = updatefunc

        # top level window
        self.textWindow = tk.Toplevel()
        self.textWindow.grab_set()

        # textbox for window
        self.textBox = tk.Text(self.textWindow, font = "Calibri")
        self.textBox.insert(index = "1.0", chars = runningReceipt)
        self.textBox.pack()

        self.initsaveButton()

    def initsaveButton(self):
        saveButton = tk.Button(self.textWindow, 
                               text = "Save", 
                               command = lambda: self.saveReceiptPressed(self.textBox.get(index1 = "1.0", index2 = tk.END)))
        saveButton.pack()

    def saveReceiptPressed(self, text):
        self.updatefunc(text)
        self.textWindow.destroy()

class ReceiptSelectWindow:
    def __init__(self, items, buyers, updatefunc):
        # top level window
        self.textWindow = tk.Toplevel()

        self.maxRow = 6 * (2 + len(buyers))
        self.currentRow = 0
        self.currentCol = 0

        self.updatefunc = updatefunc

        self.items = items
        self.buyers = buyers
        self.res = []
        self.initButtons()
            
    def initButtons(self):
        for i in range(len(self.items[0:len(self.items) - 1])): # excluding the final item as the final item is the grand total
            if self.currentRow == self.maxRow: 
                self.currentRow = 0
                self.currentCol += 1
            itemText = tk.Label(self.textWindow, text = self.items[i].formatName())
            itemText.grid(column = self.currentCol, row = self.getRow())
            self.res.append(tk.StringVar()) # initializes the variable used for retrieving user input
            self.res[i].set("Shared") # sets the default value as "shared"
            tk.Radiobutton(self.textWindow, text = "Shared", value = "Shared", variable = self.res[i]).grid(column = self.currentCol, row = self.getRow())
            for buyer in self.buyers:
                tk.Radiobutton(self.textWindow, text = buyer, value = buyer, variable = self.res[i]).grid(column = self.currentCol, row = self.getRow())
        saveButton = tk.Button(self.textWindow,
                               text = "Save",
                               command = self.saveBuyersPressed)
        saveButton.grid(column = self.currentCol, row = self.maxRow)

    def getRow(self):
        self.currentRow += 1
        return(self.currentRow)
    
    def saveBuyersPressed(self):
        self.updatefunc(list(map(lambda x: x.get(), self.res)))

        self.textWindow.destroy()

## INITIALIZING THE FIRST DATA FRAME - adding buttons, etc.
root = tk.Tk()
MainWindow(root, ["Michael", "Jackson"], "shared-costs-updating-20338dd91842.json")
root.mainloop()