public class V7 { public static void main(String[] a) throws Exception {
  for (String n : new String[]{"kr.kjmn.clashmc.Battle","kr.kjmn.clashmc.Battle$Outline","kr.kjmn.clashmc.ClashPlugin","kr.kjmn.clashmc.GameListener","kr.kjmn.clashmc.Clash","kr.kjmn.clashmc.CardDef","kr.kjmn.clashmc.Arena","kr.kjmn.clashmc.Combatant","kr.kjmn.clashmc.Bars","kr.kjmn.clashmc.Lobby","kr.kjmn.clashmc.Lobby$Portal","kr.kjmn.clashmc.PackHost","kr.kjmn.clashmc.PackMerge"}) {
    Class<?> c = Class.forName(n, true, V7.class.getClassLoader()); c.getDeclaredMethods(); } System.out.println("all verified"); } }
