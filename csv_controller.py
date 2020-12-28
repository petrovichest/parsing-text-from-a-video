import csv


def csv_reader():
    with open('./save.csv', "r", encoding='utf-8') as f_obj:
        rows = [re for re in csv.reader(f_obj, delimiter=';')]
    return rows


def csv_cleaner():
    with open('./save.csv', "w", newline='') as f:
        pass
    return


def csv_writer(data):
    with open('./save.csv', "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        for line in data:
            writer.writerow(line)
    return


if __name__ == "__main__":
    data = [[1, 2, 3], [2], [3]]
    print(csv_reader())
