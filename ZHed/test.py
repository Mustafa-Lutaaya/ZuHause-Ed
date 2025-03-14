def count_letters_and_digits(s):
    List = []
    for i in s:
        if i.isdigit() or i.isalpha():
            List.append(i)
    total = len(List)    
    return total

j = ("aj11jdjd_!AAS")

count_letters_and_digits(j)