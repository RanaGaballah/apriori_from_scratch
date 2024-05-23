import pandas as pd
from tkinter import *
from tkinter import filedialog
from collections import Counter
from itertools import combinations


def read_transactions(filename):
    """Read transactions from a file and return them in Dict Format."""
    if filename.lower().endswith('.csv'):
        data = pd.read_csv(filename)
    elif filename.lower().endswith(('.xls', '.xlsx')):
        data = pd.read_excel(filename)
    elif filename.lower().endswith('.txt'):
        data = pd.read_csv(filename, delimiter='\t')
    else:
        raise ValueError(
            "Unsupported file format. Only Excel, text, or CSV files are supported.")

    data_dict = data.groupby(data.columns[0])[
        data.columns[1]].apply(list).to_dict()
    return [[k, v] for k, v in data_dict.items()]


def generate_association_rules(frequent_itemsets, data):
    association_rules = []

    for frequent_itemset in frequent_itemsets:
        if len(frequent_itemset) > 1:
            itemset_size = len(frequent_itemset)

            for i in range(1, itemset_size):
                for subset in combinations(frequent_itemset, i):
                    subset = frozenset(subset)
                    complement = frequent_itemset - subset
                    support_subset = support(complement, data)
                    confidence = support(
                        frequent_itemset, data) / support_subset * 100 if support_subset > 0 else 0

                    association_rules.append((subset, complement, confidence))

    return association_rules


def support(itemset, data):
    count = 0
    for transaction in data:
        if itemset.issubset(set(transaction[1])):
            count += 1
    return count


def process_data():
    filename = filedialog.askopenfilename()
    min_support_percentage = float(min_support_entry.get())
    min_confidence_percentage = float(min_confidence_entry.get())
    data_percentage = float(data_percentage_entry.get())

    data = read_transactions(filename)
    total_transactions = len(data)
    data_to_analyze = int(data_percentage / 100 * total_transactions)
    data = data[:data_to_analyze]

    min_support_count = min_support_percentage
    min_confidence = min_confidence_percentage / 100

    init = []
    for i in data:
        for q in i[1]:
            if q not in init:
                init.append(q)
    init = sorted(init)
    #counts the occurrences of each item.
    c = Counter()
    for i in init:
        for d in data:
            if i in d[1]:
                c[i] += 1
    #filters out the items that meet the minimum support count
    l = Counter()
    for i in c:
        if c[i] >= min_support_count:
            l[frozenset([i])] += c[i]
    #iteratively generates larger candidate itemsets (nc) by joining the previous frequent itemsets.
    pl = l
    pos = 1
    for count in range(2, 1000):
        nc = set()
        temp = list(l)
        for i in range(0, len(temp)):
            for j in range(i + 1, len(temp)):
                t = temp[i].union(temp[j])
                if len(t) == count:
                    nc.add(temp[i].union(temp[j]))
        nc = list(nc)
        c = Counter()
        for i in nc:
            c[i] = 0
            for q in data:
                temp = set(q[1])
                if i.issubset(temp):
                    c[i] += 1

        l = Counter()
        for i in c:
            if c[i] >= min_support_count:
                l[i] += c[i]

        if len(l) == 0:
            break
        pl = l
        pos = count

    frequent_itemsets = list(pl.keys())
    association_rules = generate_association_rules(frequent_itemsets, data)

    result_text.delete('1.0', END)
    result_text.insert(END, "---------------------------------------- Final Result ---------------------------------------- \n")
    result_text.insert(END, "Candidate Itemset Table Number (" + str(pos) + ") :\n")
    result_text.insert(END, "\n")
    for itemset, support_count in pl.items():
        result_text.insert(END, str(list(itemset)) + ": " + str(support_count) + "\n")
        result_text.insert(END, "\n")  
    result_text.insert(END, "-------------------------------------------------------------------------------------------")
    result_text.insert(END, "\nAll Association Rules:\n")
    rule_number = 1
    for rule in association_rules:
        rule_text = f"{rule_number} - {list(rule[1])} -> {list(rule[0])} = {rule[2]}%\n"
        result_text.insert(END, rule_text)
        rule_number += 1
    result_text.insert(END, "-------------------------------------------------------------------------------------------")
    result_text.insert(END, "\nStrong Rules (confidence >= " + str(min_confidence_percentage) + "%):\n")
    strong_rules_indices = []
    strong_rule_number = 1
    for rule in association_rules:
        if rule[2] >= min_confidence_percentage:
            strong_rule_text = f"{strong_rule_number} - {list(rule[1])} -> {list(rule[0])} = {rule[2]}%\n"
            result_text.insert(END, strong_rule_text)
            strong_rules_indices.append(strong_rule_number)
            strong_rule_number += 1

    if not strong_rules_indices:
        result_text.insert(END, "None\n")
    result_text.insert(END, "-------------------------------------------------------------------------------------------")
    # Output the number of transaction in the file and the number of processed rows
    result_text.insert(END, "\nNumber of transaction in file: " + str(total_transactions) + "\n")
    result_text.insert(END, "Number of processed transactions: " + str(len(data)) + "\n")
    result_text.insert(END, "-------------------------------------------------------------------------------------------")

root = Tk()
root.title("Association Rule Mining")

# Labels
Label(root, text="Minimum Support Count :").grid(
    row=0, column=0, padx=10, pady=5, sticky=W)
Label(root, text="Minimum Confidence (%):").grid(
    row=1, column=0, padx=10, pady=5, sticky=W)
Label(root, text="Percentage of Data to Analyze (%):").grid(
    row=2, column=0, padx=10, pady=5, sticky=W)

# Entry fields
min_support_entry = Entry(root, width=40)
min_support_entry.grid(row=0, column=1, padx=10, pady=5, sticky=W)
min_confidence_entry = Entry(root, width=40)
min_confidence_entry.grid(row=1, column=1, padx=10, pady=5, sticky=W)
data_percentage_entry = Entry(root, width=40)
data_percentage_entry.grid(row=2, column=1, padx=10, pady=5, sticky=W)


# Button to process data
process_button = Button(root, text="Choose File",
                        command=process_data, bg="#DAF7A6", fg="black", padx=10, pady=5)
process_button.grid(row=3, column=0, columnspan=2, pady=10)

# Result text area
result_text = Text(root, width=100, height=30, bg="white")
result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()
