package main;

import hadoop.HadoopInterface;

import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import soot.Body;
import soot.BodyTransformer;
import soot.RefType;
import soot.SootMethod;
import soot.Unit;
import soot.Value;
import soot.jimple.Constant;
import soot.jimple.InstanceInvokeExpr;
import soot.jimple.InvokeExpr;
import soot.jimple.Stmt;
import soot.jimple.StringConstant;
import soot.util.Chain;

public class ConschkPass extends BodyTransformer {

  @Override
  protected void internalTransform(Body body, String phase, Map<String, String> options) {
    SootMethod method = body.getMethod();
    Chain<Unit> units = body.getUnits();
    Iterator<Unit> stmtIt = units.snapshotIterator();
    while (stmtIt.hasNext()) {
      Stmt stmt = (Stmt)stmtIt.next();
      if (!stmt.containsInvokeExpr()) {
        continue;
      }
      
      InvokeExpr expr = stmt.getInvokeExpr();
      List<Value> args = expr.getArgs();
      if (args.size() <= 1) continue;  // if size is 1, then we cannot get the default value
      
      List<Constant> consl = getConstants(args);
      if (consl.size() == 0) continue; // same thing
      
      if (expr.getMethod().getDeclaringClass().getName().contains("DeprecationDelta")) continue; //special case
      
      if (isLogger(expr)) continue;
      
      if (HadoopInterface.isGetter(expr)) { // invoke expr that has predefined getter patterns
        Value arg0 = args.get(0);
        if (arg0 instanceof StringConstant) {
          if (consl.size() == args.size()) {
            dump(true, method, expr, 0);
            continue;
          }
        }
      }
      
      // Otherwise, we apply a heuristic for exprs that do not call the getter functions
      int pIndex = -1;
      for (int i = 0; i < args.size(); i ++) {
        Value arg = args.get(i);
        if (arg instanceof StringConstant) {
          String argstr = ((StringConstant) arg).value;
          if (Conschk.pset.contains(argstr)) {
            pIndex = i;
            break;
          }
        }
      }
      if (pIndex != -1) { // contains a parameter name
        dump(false, method, expr, pIndex);
      }
    }
  }
  
  protected boolean isLogger(InvokeExpr iexpr) {
    if (iexpr instanceof InstanceInvokeExpr) {
      Value base = ((InstanceInvokeExpr) iexpr).getBase();
      if (base.getType() instanceof RefType) {
        RefType rty = (RefType) base.getType();
        if (rty.getClassName().contains("Logger")) {
          return true;
        }
      }
    }
    return false;
  }
  
  protected List<Constant> getConstants(List<Value> args) {
    LinkedList<Constant> cl = new LinkedList<Constant>();
    for (Value arg : args) {
      if (arg instanceof Constant) {
        cl.addLast((Constant) arg);
      }
    }
    return cl;
  }

  protected void dump(boolean valid, SootMethod method, InvokeExpr iexpr, int stIndex) {
    String flag = valid ? "T\n" : "F\n";
    String logl = flag;
    logl += method.getDeclaringClass().getName().toString() + "\n";
    logl += method.getSignature().toString() + "\n";
    logl += iexpr.getMethod().toString() + "\n";
    String argl = "";
    List<Value> args = iexpr.getArgs();
    for (int i = stIndex; i < args.size(); i++) {
      Value arg = args.get(i);
      if (arg instanceof Constant) {
        String argStr = arg.toString();
        if (argStr.length() == 0) {
          argStr = "null";
        }
        argl += (argStr + "\t");
      }
    }
    
    logl += argl + "\n";
    
    Conschk.output.print(logl);
  }
}
