/*
 * Soot - a J*va Optimization Framework Copyright (C) 1997-1999 Raja Vallee-Rai
 * 
 * This library is free software; you can redistribute it and/or modify it under the terms of the
 * GNU Lesser General Public License as published by the Free Software Foundation; either version
 * 2.1 of the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
 * even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License along with this library;
 * if not, write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
 * 02111-1307, USA.
 */

/*
 * Modified by the Sable Research Group and others 1997-1999. See the 'credits' file distributed
 * with Soot for the complete list of contributors. (Soot is distributed at
 * http://www.sable.mcgill.ca/soot)
 */

/* Reference Version: $SootVersion: 1.beta.6.dev.51 $ */

package main;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.HashSet;
import java.util.List;

import soot.*;


public class Conschk {
  private static final String TMP_OUTPUT = "p.get.log";
  private static final String PARAM_LIST = "p.list";
  
  public static HashSet<String> pset = new HashSet<String>();
  
  public static PrintWriter output;

  protected static void init() {
    try {
      output = new PrintWriter(new File(TMP_OUTPUT));
    	
      BufferedReader br = new BufferedReader(new FileReader(PARAM_LIST));
      String line;
      while ((line = br.readLine()) != null) {
        pset.add(line.trim().toLowerCase());
      }
      br.close();
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
  
  public static void main(String[] args) {
    init();
    run(args);
  }
  
  public static void run(String[] args) {
    String[] cfg = CheckerConfig.CONFIGS[CheckerConfig.CFG_RUN];
    
    String classPath  = CheckerConfig.getClassPath(cfg);
    List<String> srcPaths = CheckerConfig.getSourcePath(cfg);
    
    System.out.println(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PRINT CONFIGURATIONS:");
    System.out.println("CLASS PATH:  " + classPath);
    for (String s : srcPaths) {
      System.out.println("SOURCE PATH: " + s);
    }
    
    String[] initArgs = {
        "-cp", classPath, 
        "-pp", 
        "-allow-phantom-refs", 
        "-app", 
        "all-reachable",
        "-f", "n",
    };
    
    String[] sootArgs = new String[initArgs.length + 2 * srcPaths.size()];
    for (int i = 0; i < initArgs.length; i++) {
      sootArgs[i] = initArgs[i];
    }
    for (int i = 0; i< srcPaths.size(); i++) {
      sootArgs[initArgs.length + 2*i] = "-process-dir";
      sootArgs[initArgs.length + 2*i + 1] = srcPaths.get(i);
    }
    
    for (String s : sootArgs) {
      System.out.println(s);
    }
    
    PackManager.v().getPack("jtp").add(new Transform("jtp.conschk", new ConschkPass()));

    soot.Main.main(sootArgs);
    Conschk.output.flush();
    Conschk.output.close();
    
    new File(TMP_OUTPUT).renameTo(new File("plogs/p." + cfg[1] +  ".log"));
  }
}
