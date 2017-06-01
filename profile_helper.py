from inference_handler import query_once
import codecs

def approach_one(test = False):
    with codecs.open("/data/dev/sms_abbrs.source", encoding="utf-8") as f1:
        source_lines = f1.readlines()
    with codecs.open("/data/dev/sms_abbrs.target", encoding="utf-8") as f2:
        target_lines = f2.readlines()
    assert len(source_lines) == len(target_lines)

    bound = len(source_lines)
    if (test):
        bound = 10
    print("bound is", bound)
    for i in range(0, bound):
        prediction_result = query_once(source_lines[i].strip())
        for sublist in prediction_result:
            # sort the sublist so that the highest prob is at the front;
            # this is to deal with duplicate chars with different probs
            sorted_sublist = sorted(sublist, key=lambda x: x[1], reverse=True)
            found = False
            for (chars, prob) in sorted_sublist:
                # only record the probability of correctly predicted sequence
                if (chars == target_lines[i].strip()):
                    # filename format: length of correctly predicted sequence .profile
                    #print("found target!")
                    # get rid of the spaces between characters
                    filename = str(len("".join(chars.split(" ")))) + ".profile"
                    with codecs.open('profile/' + filename, 'a+', encoding='utf-8') as ff:
                        ff.write(str(prob) + "\n")
                    found = True
                    break

            if (found):
                break

def approach_two(test = False):
    with codecs.open("/data/dev/sms_abbrs.source", encoding="utf-8") as f1:
        source_lines = f1.readlines()
    with codecs.open("/data/dev/sms_abbrs.target", encoding="utf-8") as f2:
        target_lines = f2.readlines()
    assert len(source_lines) == len(target_lines)

    bound = len(source_lines)
    if (test):
        bound = 10
    print("bound is", bound)
    for i in range(0, bound):
        prediction_result = query_once(source_lines[i].strip())
        for sublist in prediction_result:
            # sort the sublist so that the highest prob is at the front;
            # this is to deal with duplicate chars with different probs
            sorted_sublist = sorted(sublist, key=lambda x: x[1], reverse=True)
            found = False
            prev_prob = 0
            for (chars, prob) in sorted_sublist:
                if (chars == target_lines[i].strip()):
                    delta = 0
                    if (prev_prob != 0):
                        delta = prob - prev_prob
                    #print("found target!", "delta is:", delta)
                    # get rid of the spaces between characters
                    # filename format: length of correctly predicted sequence .profile.delta
                    filename = str(len("".join(chars.split(" ")))) + ".profile.delta"
                    with codecs.open('profile/' + filename, 'a+', encoding='utf-8') as ff:
                        ff.write(str(delta) + "\n")
                    found = True
                    break
                else:
                    prev_prob = prob

            if (found):
                break

if __name__ == "__main__":
    #approach_one(False)
    approach_two()

