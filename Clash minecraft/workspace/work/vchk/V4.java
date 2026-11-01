public class V4 { public static void main(String[] a) throws Exception {
  for (String n : new String[]{"kr.kjmn.clashmc.Combatant","kr.kjmn.clashmc.Battle","kr.kjmn.clashmc.CardDef","kr.kjmn.clashmc.Clash","kr.kjmn.clashmc.Arena","kr.kjmn.clashmc.GameListener","kr.kjmn.clashmc.ClashPlugin"}) {
    Class<?> c = Class.forName(n, true, V4.class.getClassLoader()); c.getDeclaredMethods(); System.out.println("verified " + n); } } }
