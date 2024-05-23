import pandas as pd
from tkinter import *
from tkinter import filedialog
from collections import Counter
from itertools import combinations


def read_scores(filename):
    """Read scores from the provided file."""
    if filename.lower().endswith('.csv'):
        data = pd.read_csv(filename)
    elif filename.lower().endswith(('.xls', '.xlsx')):
        data = pd.read_excel(filename)
    elif filename.lower().endswith('.txt'):
        data = pd.read_csv(filename, delimiter='\t')
    else:
        raise ValueError(
            "Unsupported file format. Only Excel, text, or CSV files are supported.")

    return data.values.tolist()


def process_data():
    filename = filedialog.askopenfilename()
    min_support_count = int(min_support_entry.get())
    min_confidence_percentage = float(min_confidence_entry.get())
    data_percentage = float(data_percentage_entry.get())

    data = read_scores(filename)
    total_students = len(data)
    data_to_analyze = int(data_percentage / 100 * total_students)
    data = data[:data_to_analyze]

    item_counts = Counter()
    for scores in data:
        for score in scores:
            item_counts[score] += 1

    min_confidence = min_confidence_percentage / 100

    init = []
    for i in data:
        for q in i:
            if q not in init:
                init.append(q)
    init = sorted(init)

    c = Counter()
    for i in init:
        for d in data:
            if i in d:
                c[i] += 1

    l = Counter()
    for i in c:
        if c[i] >= min_support_count:
            l[frozenset([i])] += c[i]

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
                temp = set(q)
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

    result_text.delete('1.0', END)
    result_text.insert(END, "Final Result: \n")
    result_text.insert(
        END, "Candidate Itemset Table Number " + str(pos) + ":\n")
    for i in pl:
        result_text.insert(END, str(list(i)) + ": " + str(pl[i]) + "\n")
    result_text.insert(END, "\n")

    for l in pl:
        c = [frozenset(q) for q in combinations(l, len(l) - 1)]
        mmax = 0
        for a in c:
            b = l - a
            ab = l
            sab = 0
            sa = 0
            sb = 0
            for q in data:
                temp = set(q)
                if a.issubset(temp):
                    sa += 1
                if b.issubset(temp):
                    sb += 1
                if ab.issubset(temp):
                    sab += 1
            temp = sab / sa * 100
            if temp > mmax:
                mmax = temp
            temp = sab / sb * 100
            if temp > mmax:
                mmax = temp
            result_text.insert(END, str(list(a)) + " -> " +
                               str(list(b)) + " = " + str(sab / sa * 100) + "%\n")
            result_text.insert(END, str(list(b)) + " -> " +
                               str(list(a)) + " = " + str(sab / sb * 100) + "%\n")
        curr = 1
        result_text.insert(END, "Strong Rules (confidence >= " +
                           str(min_confidence_percentage) + "%) Rule Number: ")
        for a in c:
            b = l - a
            ab = l
            sab = 0
            sa = 0
            sb = 0
            for q in data:
                temp = set(q)
                if a.issubset(temp):
                    sa += 1
                if b.issubset(temp):
                    sb += 1
                if ab.issubset(temp):
                    sab += 1
            temp = sab / sa * 100
            if temp >= min_confidence_percentage:
                result_text.insert(END, str(curr) + " ")
            curr += 1
            temp = sab / sb * 100
            if temp >= min_confidence_percentage:
                result_text.insert(END, str(curr) + " ")
            curr += 1
        result_text.insert(END, "\n\n")

    # Output the number of students in the file and the number of processed students
    result_text.insert(END, "Number of students in file: " +
                       str(total_students) + "\n")
    result_text.insert(END, "Number of processed students: " +
                       str(len(data)) + "\n")


root = Tk()
root.title("Association Rule Mining")

# Labels
Label(root, text="Minimum Support Count:").grid(
    row=0, column=0, padx=10, pady=5, sticky=W)
Label(root, text="Minimum Confidence (%):").grid(
    row=1, column=0, padx=10, pady=5, sticky=W)
Label(root, text="Percentage of Data to Analyze (%):").grid(
    row=2, column=0, padx=10, pady=5, sticky=W)

# Entry fields
min_support_entry = Entry(root, width=10)
min_support_entry.grid(row=0, column=1, padx=10, pady=5)
min_confidence_entry = Entry(root, width=10)
min_confidence_entry.grid(row=1, column=1, padx=10, pady=5)
data_percentage_entry = Entry(root, width=10)
data_percentage_entry.grid(row=2, column=1, padx=10, pady=5)

# Button to process data
process_button = Button(root, text="Choose File",
                        command=process_data, bg="#DAF7A6", fg="black")
process_button.grid(row=3, column=0, columnspan=2, pady=10)

# Result text area
result_text = Text(root, width=60, height=20, bg="white")
result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

root.mainloop()
