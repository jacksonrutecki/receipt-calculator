# receipt calculator, 09.15.23
# takes in a star market receipt (copied from "Order Date" and downwards 
# until the final total, and splits it based on what me and michael owe)

from oauth2client.service_account import ServiceAccountCredentials
from readFileToArray import *

def receiptcalc(receiptString):
    # GroceryItem class that represents an item in a grocery store
    # name -- name of the grocery store item
    # cost -- cost of the grocery store item
    class GroceryItem:
        def __init__(self, name, cost):
            self.name = name
            self.cost = cost

        def formatName(self):
            return("- " + self.name + " ($" + str(self.cost) + ")\n")

    # read the receipt into an array with each line of the receipt being an index in the array
    #receiptString = readFileToArray("fullReceipt.txt")

    # take the receipt, and sort it into a list of grocery items with an associated name and cost
    # NOTE: this can be abstracted into a function to potentially work with multiple different kinds of receipts
    receiptItems = []
    for i in range(len(receiptString)):
        if receiptString[i] == "Payment Details": # terminate at the end of the receipt
            break

        # differentiate between regular price and sale prices
        if receiptString[i + 1] == "Regular Price":
            cost = 0
            if receiptString[i + 3] == "Savings":
                cost = float(receiptString[i + 8][1:])
            else:
                cost = float(receiptString[i + 4][1:])
            receiptItems.append(GroceryItem(receiptString[i], cost))
        
        if receiptString[i] == "ADDITIONAL DISCOUNTS":
            if not('Member/4u Savings\t' in receiptString[i + 1]):
                midIndex = receiptString[i+1].index("\t")
                receiptItems.append(GroceryItem(receiptString[i + 1][0:midIndex], -1 * float(receiptString[i + 1][(midIndex + 3):])))

    finalTotal = float(receiptString[len(receiptString) - 2][1:])
    studentDisc = finalTotal * 0.05
    receiptItems.append(GroceryItem("Student Discount", (-1 * studentDisc)))
    receiptItems.append(GroceryItem("Final Total", finalTotal))

    return(receiptItems)