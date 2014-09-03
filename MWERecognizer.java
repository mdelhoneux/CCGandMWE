/*****************************************************************
 * @author: Miryam de Lhoneux, mdelhoneux@gmail.com
 * @ note: this code is based on complexDetectorExample in the user's guide)
 * @note: feel free to send me an email if you have any question
 * This code is not copyrighted but if used, please cite
 * de Lhoneux, M. (2014). CCG Parsing and Multiword Expressions. Master's thesis, University of Edinburgh.
 * @notebis: I'm sorry for the aweful look of this code, it was my first java program
 * Implementation of the jMWE detector
 * Input: a sentence (argument)
 * Output: (to system) a list of MWEs with MWE units joined by an
 * underscore and MWEs separated by a space
 * Package required: edu.mit.jmwe
 *****************************************************************/
import edu.mit.jmwe.detect.*;
import edu.mit.jmwe.detect.StopWords;

import edu.mit.jmwe.index.*;
import edu.mit.jmwe.data.*;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.Date;

public class MWERecognizer{
	// Constructor
	IMWEIndex index;
	File idxData;
	IMWEDetector detector;
	MaxentTagger tagger;
	public MWERecognizer(IMWEDetector detector) throws IOException {
		this.detector = detector;
		this.tagger = new MaxentTagger("models/wsj-0-18-left3words-distsim.tagger");
	}

	// recognise method
	public List <String> MWERecognize(List <IToken> sentence) throws IOException {
		/*Function: recognise MWEs in a sentence
		 * Input: a sentence as a list of ITokens
		 * Output: a list of MWEs where units are joined by an underscore
		 */
		List <String> MWE = new ArrayList<String>();
		for(IMWE <IToken > mwe : detector.detect(sentence)) {
			MWE.add(mwe.getForm() );
		}
		return MWE;
	}
	public String RecognizeSentence(String sentence) throws IOException {
		/*Function: detect MWEs in a sentence
		 * Input: a sentence as string
		 * Output: (currently to system) MWEs separated by spaces
		 */
		String mwes = "";
		String tagged = tagger.tagString(sentence);

		List <IToken > ISentence = new ArrayList <IToken >() ;
		for (String Tw : tagged.split(" ")){
			String[] WordAndTag = Tw.split("_");
			String word = WordAndTag[0];
			String tag = WordAndTag[1];
			try{
				ISentence.add(new Token (word,tag));
			}catch(IllegalArgumentException E){

			}

		}
		// Recognise sentence

		List <String> MWE = MWERecognize(ISentence);
		for (String mwe: MWE){
			mwes += mwe;
			mwes += " ";
		}
		return mwes;
	}

	public static void main(String args[]) throws IOException {
		// 1/ get handle to file containing MWE index data 
		//TODO parametrise
		long lStartTime = new Date().getTime();
		File idxData = new File("mweindex_wordnet3.0_semcor1.6.data");
		IMWEIndex index = new MWEIndex(idxData);
		index.open();
		
		//2/ construct the detector
		//IMWEDetector d1 = new StopWords();
		// make detectors
		IMWEDetector pnDetector = ProperNouns.getInstance();
		//IMWEDetector goodDetector = new MoreFrequentAsMWE(new InflectionPattern(new Consecutive(index)));
		//IMWEDetector d1 = new Continuous(new TrulyExhaustive(index));
		IMWEDetector d1 = new Continuous(pnDetector); //best
		
		
		//IMWEDetector detector1 = new CompositeDetector(pnDetector, goodDetector);
		//IMWEDetector detector1 = new MoreFrequentAsMWE(new Consecutive(index));
		Longest detector = new Longest(d1); //best
		//LMLR detector = new LMLR(d1);
		
		MWERecognizer Recognizer = new MWERecognizer(detector);
		
		/*
		 * Write description file
		 */
		String CCGMWes = args[0];
		String CCGbank_raw = args[1];
		File CCGbank_MWEs = new File(CCGMWes);
		if (!CCGbank_MWEs.exists()) CCGbank_MWEs.mkdir();
		String DescriptionFilestr = CCGMWes + "/description.txt";
		File DescriptionFile = new File(DescriptionFilestr);
		PrintWriter descr = new PrintWriter(DescriptionFile);
		String description = "MWE Detectors used:\n" + "\n" + d1.toString() + "\n" + 
		detector.toString() + "\n" + "MWE index used:\n" + idxData.toString() + "\n";
		descr.write(description);
		
		/*
		 * Recognise Treebank
		 */
		

		String pattern = "ID=wsj";
		Pattern r = Pattern.compile(pattern);
		File CCGbank = new File(CCGbank_raw);
		File[] CCGsections = CCGbank.listFiles();

		for (File CCGsection : CCGsections) {
			File[] CCGfiles = CCGsection.listFiles();
			String CCGsectnumber = CCGsection.toString();
			CCGsectnumber = CCGsectnumber.substring(CCGsectnumber.length() - 2);
			String CCGsect = CCGMWes + CCGsectnumber;
			File CCGsectf = new File(CCGsect);
			if (!CCGsectf.exists()) CCGsectf.mkdir();
			for (File CCGfile : CCGfiles) {
				if (CCGfile.isFile()) {	
					String filen = CCGfile.toString();
					filen = filen.substring(filen.length() - 12, filen.length() - 4) + ".mwe";
					String filename = CCGsect + "/" + filen;
					PrintWriter out = new PrintWriter(filename);
					BufferedReader in = new BufferedReader(new FileReader(CCGfile));
					while (in.ready()) {
						String s = in.readLine();
						Matcher m = r.matcher(s);
						if (m.find()) out.println(s);
						else {
							String sentence = s;
							String mwes = Recognizer.RecognizeSentence(sentence);
							out.print(mwes + "\n");
							out.flush();
						}

					}
					in.close();
					out.close();
				}
			}
		}
		long lEndTime = new Date().getTime();
		long difference = lEndTime - lStartTime;
		descr.write("Time of execution " + difference + " milliseconds\n");
		descr.close();
	}	 
}
