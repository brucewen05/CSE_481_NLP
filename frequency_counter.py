import pinyin_util as pu
import codecs


def generate_count_file(output_filename, char_filename = "/data/weibo.txt"):
    with codecs.open(char_filename, encoding='utf-8') as f:
        lines = f.readlines()
    all_chars = pu.get_all_candidates_chars()

    result = {}
    for line in lines:
        for char in line:
            if (char in all_chars):
                if (char in result):
                    result[char] += 1
                else:
                    result[char] = 1
    print("writing result to", output_filename, "...")
    with codecs.open(output_filename, 'a+', encoding='utf-8') as ff:
        for char, count in result.items():
            ff.write(char + "\t" + str(count) + "\n")
    print("done writing the map...")

def load_count_map(map_file):
    print("Loading count map from", map_file, "...")
    result = {}
    with codecs.open(map_file, encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        key_value = line.strip().split("\t")
        result[key_value[0]] = int(key_value[1])
    return result
        

if __name__ == "__main__":
    generate_count_file("/data/weibo_count.txt")
    #generate_count_file("test.txt", char_filename = "./testfile")
    #result = load_count_map("test.txt")
    #print(result)

