// node risu_css.cjs < 배경.css   (이 폴더에서 npm install @adobe/css-tools@4.4.4 postcss-selector-parser@7.1.1)
// RisuAI parser.svelte.ts decodeStyleContent / decodeStyleRule, run with the same libraries
const css = require('@adobe/css-tools');
const cssSelectorParser = require('postcss-selector-parser');
function decodeStyleRule(rule) {
  if (rule.type === 'rule' && rule.selectors) {
    for (let i = 0; i < rule.selectors.length; i++) {
      let slt = rule.selectors[i];
      if (slt) {
        const parser = cssSelectorParser((root) => {
          root.walkClasses((classes) => {
            if (classes.type === 'class' && !classes.value.startsWith('x-risu-')) classes.value = 'x-risu-' + classes.value;
          });
        });
        slt = parser.processSync(slt);
        rule.selectors[i] = '.chattext ' + slt;
      }
    }
  }
  if (['media', 'supports', 'document', 'host', 'container'].includes(rule.type)) {
    for (let i = 0; i < rule.rules.length; i++) rule.rules[i] = decodeStyleRule(rule.rules[i]);
  }
  if (rule.type === 'import' && rule.import.startsWith('data:')) rule.import = 'data:,';
  return rule;
}
const text = require('fs').readFileSync(0, 'utf8');
const ast = css.parse(text);
ast.stylesheet.rules = ast.stylesheet.rules.map(decodeStyleRule);
process.stdout.write(css.stringify(ast, { indent: '', compress: true }));
