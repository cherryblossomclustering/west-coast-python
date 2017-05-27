import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.lang.System;
import java.util.*;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.trees.TreeGraphNode;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Properties;

public class ParserCompressor{
    /* A class that just outputs a statistically like syntax tree for a sentence. */

    public static void main(String[] args)
    {

        PrintStream err = System.err;

        // now make all writes to the System.err stream silent
        System.setErr(new PrintStream(new OutputStream() {
            public void write(int b) {
            }
        }));

        Properties props = new Properties();
        props.setProperty("annotators", "tokenize, ssplit, parse");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

        Annotation document = new Annotation(args[0]);
        pipeline.annotate(document);


        List<CoreMap> sentences = document.get(SentencesAnnotation.class);
        CoreMap sentence = sentences.get(sentences.size() - 1);
        Tree tree = (Tree) sentence.get(TreeAnnotation.class);
        tree.pennPrint();
        System.setErr(err);
    }
}