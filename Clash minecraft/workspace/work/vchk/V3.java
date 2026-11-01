public class V3 { public static void main(String[] a) throws Exception {
  for (String n : new String[]{"kr.kjmn.clashmc.Combatant","kr.kjmn.clashmc.Battle","kr.kjmn.clashmc.Battle$1","kr.kjmn.clashmc.Battle$2","kr.kjmn.clashmc.Battle$3","kr.kjmn.clashmc.Battle$4","kr.kjmn.clashmc.Battle$Zone","kr.kjmn.clashmc.CardDef","kr.kjmn.clashmc.Clash","kr.kjmn.clashmc.Clash$1","kr.kjmn.clashmc.Arena","kr.kjmn.clashmc.GameListener"}) {
    Class<?> c = Class.forName(n, true, V3.class.getClassLoader()); c.getDeclaredMethods(); System.out.println("verified " + n); } } }
