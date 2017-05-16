from inference_handler import query_once
import codecs

with codecs.open("/data/dev/sms_abbrs.source", encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        prediction_result = query_once(line.strip())
        for sublist in prediction_result:
            if (len(sublist) > 0):
                predicted_sequence_length = len(sublist[0][0])
                # use the length of the character as the filename
                # so that all the predicted sequence of the same length
                # goes to the same file for comparison
                filename = str(predicted_sequence_length) + ".profile"
                sorted_sublist = sorted(sublist, key=lambda x: x[1], reverse=True)
                with codecs.open('profile/' + filename, 'a+',encoding='utf-8') as f2:
                    for (chars, prob) in sorted_sublist:
                        f2.write(line + '\t' + chars + '\t' + str(prob) + '\n')



