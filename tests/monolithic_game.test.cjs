const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const elements = new Map();
const context = vm.createContext({
  document: {querySelector: key => { if (!elements.has(key)) elements.set(key, {}); return elements.get(key); }},
  shuffleItems: values => [...values],
  selectedUserId: 1,
  localStorage: {getItem: () => 'null'},
});
vm.runInContext(fs.readFileSync('app/web/static/js/monolithic-game.js', 'utf8'), context);
const evaluate = source => vm.runInContext(source, context);
for (const [answer, expected, correct] of [
  ['ren4', 'rén', false], ['rèn', 'rén', false], ['ren2', 'rén', true], ['ren', 'rén', true],
  ['nǚ','nǚ',true], ['nv3','nǚ',true], ['nu:3','nǚ',true], ['nu3','nǚ',false], ['nu','nǚ',false],
  ['lü4','lǜ',true], ['lv4','lǜ',true], ['lu4','lǜ',false], ['le5','le',true], ['le0','le',true],
  ['le4','le',false], ['ré4n','rén',false], ['ren22','rén',false], ['', 'rén',false],
]) assert.equal(context.monoPinyinMatches(answer, expected), correct, `${answer} vs ${expected}`);
assert.equal(context.monoMeaning({meaning_vi:'đến',origin_meaning_vi:'lúa mì'}), 'đến');
assert.equal(JSON.stringify(context.readFlashMemory()), '{}');
evaluate(`var cards = [
  {simplified:'重',traditional:'重',pinyin:'zhòng',meaning_vi:'nặng',readings:[{pinyin:'zhòng'},{pinyin:'chóng'}]},
  {simplified:'虫',traditional:'蟲',pinyin:'chóng',meaning_vi:'sâu'},
  {simplified:'众',traditional:'眾',pinyin:'zhòng',meaning_vi:'nhiều'},
  {simplified:'来',traditional:'來',pinyin:'lái',meaning_vi:'đến'},
  {simplified:'至',traditional:'至',pinyin:'zhì',meaning_vi:'đến'}];`);
assert.equal(evaluate(`monoReadings(cards[0]).includes('chóng')`), true);
assert.equal(evaluate(`monoHanziMatches('來', monoTypingQuestions(cards)[3])`), true);
assert.equal(evaluate(`monoHanziMatches('至', monoTypingQuestions(cards)[3])`), true);
assert.equal(evaluate(`monoHanziMatches('木', monoTypingQuestions(cards)[3])`), false);
const questions = evaluate('monoGameQuestions(cards)');
for (const question of questions) {
  assert.equal(new Set(question.options).size, question.options.length);
  assert.ok(question.options.includes(question.correct));
}
console.log('Monolithic game regression checks passed');
