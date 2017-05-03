package nlpcapstone;

import com.hankcs.hanlp.*;
import com.hankcs.hanlp.dictionary.py.Pinyin;
import com.hankcs.hanlp.seg.Segment;
import com.hankcs.hanlp.seg.CRF.CRFSegment;
import com.hankcs.hanlp.seg.common.Term;
import com.hankcs.hanlp.tokenizer.StandardTokenizer;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;


public class PinyinUtil {
    public static void main(String[] args) throws IOException {
        Scanner sc = new Scanner(new File("input.txt"));
        List<String> output = new ArrayList<>();
        
        Segment segment = new CRFSegment();
        segment.enablePartOfSpeechTagging(false);
        
        while (sc.hasNextLine()) {
            String line = sc.nextLine();
            
            List<Term> termList = segment.seg(line);
            
            StringBuilder sb = new StringBuilder();
            for (Term term : termList) {
//                System.out.print(term.word + "|");
                sb.append(term.word + "|");
            }
//            System.out.println();
            line = sb.toString();
            
            List<Pinyin> pinyinList = HanLP.convertToPinyinList(line);
            sb = new StringBuilder();
            sb.append(line + " ==> ");
            for (int i = 0; i < pinyinList.size(); i++) {
                String py = pinyinList.get(i).getPinyinWithoutTone();
                if (py.equals("none")) {
                    sb.append(line.charAt(i) + " ");
                } else {
                    sb.append(pinyinList.get(i).getPinyinWithoutTone() + " ");
                }
            }
            output.add(sb.toString());
        }
        sc.close();
        Path file = Paths.get("output.txt");
        Files.write(file, output, Charset.forName("UTF-8"));
    }
}
