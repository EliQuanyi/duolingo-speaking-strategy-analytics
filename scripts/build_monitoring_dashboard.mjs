import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

// Dependency junction is created by the PowerShell launcher from the bundled runtime.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const qaDir = path.join(root, 'reports/generated/monitoring_build');
const require = createRequire(path.join(qaDir, 'package.json'));
const { Workbook, SpreadsheetFile, FileBlob } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
await fs.mkdir(qaDir, { recursive: true });
if (process.argv.includes('--help-print')) {
  const helpBook = Workbook.create(); helpBook.worksheets.add('Help');
  console.log(helpBook.help('worksheet.pageLayout', {include:'index,examples,notes',maxChars:5000}).ndjson);
  console.log(helpBook.help('workbook.render', {include:'index,examples,notes',maxChars:5000}).ndjson);
  process.exit(0);
}
if (process.argv.includes('--render-saved')) {
  const saved = await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root, 'reports/strategy_dashboard.xlsx')));
  saved.recalculate();
  for (const [name,end,file] of [['证据与就绪',40,'monitoring_evidence.png'],['未来KPI',30,'monitoring_kpi.png']]) {
    const blob = await saved.render({sheetName:name,range:`A1:J${end}`,scale:1.5,format:'png',headers:false});
    await fs.writeFile(path.join(qaDir,file), new Uint8Array(await blob.arrayBuffer()));
  }
  const errors = await saved.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:3000});
  await fs.writeFile(path.join(qaDir,'monitoring_reimport_qa.json'),JSON.stringify({status:saved.worksheets.getItem('未来KPI').getRange('B5').values[0][0],errors:errors.ndjson,source:'Final saved XLSX reimported; these renders are PDF source images.'},null,2));
  console.log('Rendered final saved XLSX with row/column headers off.');
  process.exit(0);
}
if (process.argv.includes('--render-pdf')) {
  const canvasApi = require('@napi-rs/canvas');
  globalThis.DOMMatrix = canvasApi.DOMMatrix; globalThis.ImageData = canvasApi.ImageData; globalThis.Path2D = canvasApi.Path2D;
  const pdfjs = await import(pathToFileURL(require.resolve('pdfjs-dist/legacy/build/pdf.mjs')).href);
  const pdf = await pdfjs.getDocument({data:new Uint8Array(await fs.readFile(path.join(root,'reports/strategy_dashboard.pdf'))),standardFontDataUrl:path.join(path.dirname(require.resolve('pdfjs-dist/package.json')),'standard_fonts').replaceAll('\\','/') + '/'}).promise;
  if(pdf.numPages !== 2) throw new Error('PDF page count differs from two-sheet snapshot.');
  for(let pageIndex=1;pageIndex<=pdf.numPages;pageIndex++) {
    const page = await pdf.getPage(pageIndex); const viewport = page.getViewport({scale:1.8});
    const canvas = canvasApi.createCanvas(Math.ceil(viewport.width),Math.ceil(viewport.height));
    await page.render({canvasContext:canvas.getContext('2d'),viewport,intent:'print'}).promise;
    await fs.writeFile(path.join(qaDir,`monitoring_pdf_page${pageIndex}.png`),canvas.toBuffer('image/png'));
  }
  await fs.writeFile(path.join(qaDir,'monitoring_pdf_render_qa.json'),JSON.stringify({engine:'PDF.js with bundled @napi-rs/canvas',pages:pdf.numPages,actualPdfRendered:true},null,2));
  await pdf.destroy(); console.log('Rendered both actual PDF pages for visual review.'); process.exit(0);
}

async function readCsv(relative) {
  const csv = await fs.readFile(path.join(root, relative), 'utf8');
  const imported = await Workbook.fromCSV(csv, { sheetName: 'CSV' });
  const rows = imported.worksheets.getItemAt(0).getUsedRange().values;
  const headers = rows[0];
  return rows.slice(1).map(row => Object.fromEntries(headers.map((h, i) => [h, row[i]])));
}
const metrics = await readCsv('data/public/company_quarterly_metrics.csv');
const sources = await readCsv('data/source_register.csv');
const dau = metrics.filter(x => x.metric_id === 'M001').sort((a, b) => a.period_start.localeCompare(b.period_start));
if (dau.length !== 8 || dau.some(x => x.unit !== 'million users' || x.aggregation_type !== 'daily_average')) {
  throw new Error('Expected eight company-level quarterly-average DAU observations in million users.');
}

const wb = Workbook.create();
const evidence = wb.worksheets.add('证据与就绪');
const monitor = wb.worksheets.add('未来KPI');
const ink = '#18323D', muted = '#50626B', navy = '#214755';
const amber = '#FFF0CE', red = '#FBE1DE', green = '#E3F1E7';
const font = 'Microsoft YaHei';

function value(sheet, range, text) {
  const r = sheet.getRange(range);
  if (range.includes(':')) r.merge();
  r.values = [[text]];
}
function rowHeight(sheet, row, pixels) { sheet.getRange(`B${row}:I${row}`).format.rowHeightPx = pixels; }
function section(sheet, row, text) {
  value(sheet, `B${row}:I${row}`, text);
  sheet.getRange(`B${row}:I${row}`).format = { fill: '#E8EFF1', font: { name: font, size: 10, bold: true, color: ink } };
  rowHeight(sheet, row, 23);
}
function base(sheet, end) {
  sheet.showGridLines = false;
  sheet.tabColor = navy;
  sheet.getRange(`A1:J${end}`).format = { font: { name: font, size: 10, color: ink }, verticalAlignment: 'center', wrapText: true, rowHeightPx: 18 };
  sheet.getRange(`A1:A${end}`).format.columnWidthPx = 14;
  sheet.getRange(`J1:J${end}`).format.columnWidthPx = 14;
  sheet.getRange(`B1:I${end}`).format.columnWidthPx = 110;
  rowHeight(sheet, 1, 9);
  rowHeight(sheet, 2, 28);
  rowHeight(sheet, 3, 25);
  rowHeight(sheet, 4, 9);
  sheet.getRange('B2:I2').format.font = { name: font, size: 15, bold: true, color: ink };
  sheet.getRange('B3:I3').format.font = { name: font, size: 9, color: muted };
}
function statusFormatting(range) {
  // Explicit Excel formulas are required: containsText exported without its SEARCH formula.
  range.conditionalFormats.addCustom('LEFT($B$5,2)="黄色"', { fill: amber, font: { color: '#825400', bold: true } });
  range.conditionalFormats.addCustom('LEFT($B$5,2)="红色"', { fill: red, font: { color: '#9C3028', bold: true } });
  range.conditionalFormats.addCustom('LEFT($B$5,2)="绿色"', { fill: green, font: { color: '#21633A', bold: true } });
}
base(evidence, 40); base(monitor, 30);
value(evidence, 'B2:I2', 'Speaking / Video Call 扩张监控设计');
value(evidence, 'B3:I3', '外部公开资料分析。设计快照 v1.0，2026-10-03。公司数据截至 2026-06-30，证据截至 2026-10-02。');
evidence.getRange('B5:I5').merge();
evidence.getRange('B5').formulas = [["='未来KPI'!B5"]];
statusFormatting(evidence.getRange('B5:I5')); rowHeight(evidence, 5, 28);
value(evidence, 'B6:I6', '当前没有执行权益试验、采集内部结果或上线监控。H1研究任务优先，P1仍需确认真实新增资格与实施权限。');
rowHeight(evidence, 6, 29); rowHeight(evidence, 7, 8);
const headerRanges = ['B8:D8', 'E8:E8', 'F8:G8', 'H8:I8'];
['就绪条件', '当前状态', '证据与缺口', '下一行动'].forEach((x, i) => value(evidence, headerRanges[i], x));
evidence.getRange('B8:I8').format = { fill: navy, font: { name: font, size: 10, color: '#FFFFFF', bold: true } }; rowHeight(evidence, 8, 23);
const gates = [
  ['实际P0与新增权益', '未就绪', '总体Super推出陈述不能核实目标账户、角色和额度。', '先核资格表与日期。核实无增量则停止该政策定义。'],
  ['H1学习任务与迁移', '受限证据', '随机设计完成者短期信号。全员ITT、自然任务和延后迁移未知。', '优先设计同等难度前测与延后未练情境盲评。'],
  ['分配识别与实施权限', '未就绪', '没有已核随机分配、合法延后权限或冻结预案。', '有权限才设计新增访问。否则只做可实施学习研究。'],
  ['完整两臂经营与服务账单', '未就绪', '全员贡献、退款、失败重试及购买后服务成本未知。', '贡献与AI服务费分开，同窗同币种，含零使用者。'],
  ['完整政策与预算', '未就绪', '原Max传播、互斥层部署N、新增F和批准预算未知。', '缺层不设零。未补齐不判总体净值、排名或Scale。'],
];
gates.forEach((g, i) => {
  const r = 9 + i * 2;
  ['B:D', 'E:E', 'F:G', 'H:I'].forEach((span, j) => {
    const [a, b] = span.split(':'); value(evidence, `${a}${r}:${b}${r+1}`, g[j]);
  });
  evidence.getRange(`E${r}:E${r+1}`).format.fill = amber;
  evidence.getRange(`B${r}:I${r+1}`).format.borders = { bottom: { style: 'thin', color: '#D8E0E3' } };
  rowHeight(evidence, r, 19); rowHeight(evidence, r+1, 19);
});
rowHeight(evidence, 19, 8);
section(evidence, 20, '经营背景：公司DAU上升，功能增量仍需独立识别');
value(evidence, 'B21:I21', 'DAU：全球公司季度日均活跃用户，单位百万。A官方事实；采集于2026-09-30。公司趋势不提供Video Call效果或留存uplift。');
rowHeight(evidence, 21, 28); rowHeight(evidence, 22, 8);
evidence.getRange('B23:D31').values = [['季度', 'DAU（百万）', '原始来源'], ...dau.map(x => [`${x.fiscal_year} Q${x.fiscal_quarter}`, Number(x.value), x.source_id])];
evidence.getRange('B23:D23').format = { fill: navy, font: { name: font, size: 10, bold: true, color: '#FFFFFF' } };
evidence.getRange('C24:C31').setNumberFormat('0.0');
evidence.getRange('C24:C31').format.horizontalAlignment = 'right';
evidence.getRange('D24:D31').format.font = { name: font, size: 10, color: '#1E5C92', underline: 'single' };
for (let i = 23; i <= 31; i++) rowHeight(evidence, i, 22);
const provenance = dau.map((x, i) => ({ cell: `D${24+i}`, source_id: x.source_id, source_url: x.source_url,
  report_period: `${x.period_start}/${x.period_end}`, collected_on: x.collected_on || x.accessed_on,
  unit: x.unit, definition: 'Global company quarterly-average DAU. Not a Video Call measure.', source_locator: x.source_locator }));
dau.forEach((x, i) => {
  const reg = sources.find(s => s.source_id === x.source_id);
  wb.notes.add({ id: `DAU-${i}`, target: { cell: { sheetName: evidence.name, sheetId: evidence.sheetId, address: `C${24+i}` } }, authorId: '', createdAt: '',
    body: { plainText: `Source: ${reg?.title || x.source_id}. ${x.source_url}\nPeriod: ${x.period_start}/${x.period_end}. ${x.unit}; daily_average; global_company. Collected: ${x.collected_on || x.accessed_on}. Locator: ${x.source_locator}.` } });
});
const chart = evidence.charts.add('line', evidence.getRange('B23:C31'));
chart.title = '公司季度日均DAU（百万）'; chart.titleTextStyle.typeface = font; chart.titleTextStyle.fontSize = 13;
chart.hasLegend = false;
chart.xAxis = { axisType: 'textAxis', textStyle: { typeface: font, fontSize: 10 } };
chart.yAxis = { numberFormatCode: '0', numberFormatSourceLinked: false, textStyle: { typeface: font, fontSize: 11 } };
chart.series.items[0].line = { fill: '#337D91', style: 'solid', width: 2 };
chart.setPosition('E23', 'I33');
value(evidence, 'B32:D33', '来源ID对应SEC原文。完整URL、报告期和定位保存在DAU单元格备注及设计文档。');
rowHeight(evidence, 32, 20); rowHeight(evidence, 33, 20); rowHeight(evidence, 34, 8);
section(evidence, 35, '决策触发：评审与扩张分开');
const decisions = [
  ['绿色', '真实增量、权限、数据契约、预算与预案冻结齐备：可提交受限验证审批。Scale另需真实全员结果、学习/课程护栏及完整政策经济性或教学预算。', green],
  ['黄色', '字段缺失、效果未成熟或置信区间跨冻结门槛：补证或Iterate。当前保持黄色，不用公司增长或完成者学习成绩代填。', amber],
  ['红色', '核实无新增权益、权限不通过、冻结护栏明确恶化或完整费用突破批准上限：暂停/Stop，排查后重新评审。', red],
];
decisions.forEach((d, i) => { const r = 36+i; value(evidence, `B${r}:C${r}`, d[0]); value(evidence, `D${r}:I${r}`, d[1]); evidence.getRange(`B${r}:C${r}`).format.fill = d[2]; rowHeight(evidence, r, 35); });
value(evidence, 'B39:I40', '依据：quant/stage4_final_delivery.md、quant/evidence_assumptions.md、stage4经济/政策就绪CSV、analysis/business_review.md。财务窗口与功能窗口分开。当前无自动刷新。');
rowHeight(evidence, 39, 17); rowHeight(evidence, 40, 17);

value(monitor, 'B2:I2', '未来KPI：定义、阈值与行动');
value(monitor, 'B3:I3', '拟方案 v1.0。Primary为H1延后未练情境盲评score的全员ITT差。所有阈值、额度和窗口由匹配数据及审批冻结。');
value(monitor, 'B5:I5', ''); rowHeight(monitor, 5, 28);
value(monitor, 'B6:I6', '黄色输入格当前留空。填写会重算设计就绪状态；填写不生成实验结果。绿色仅表示可提交受限验证审批。'); rowHeight(monitor, 6, 28);
rowHeight(monitor, 7, 8);
const inputRows = [
  ['前测baseline均值（分）', '前测SD（分，>0）'],
  ['primary MDE（分，>0）', '学习window HL（天，>0）'],
  ['调用cap（次/账户，≥0）', '账单/预算currency'],
  ['完整批准budget cap（≥0）', '匹配数据/来源定位'],
  ['完整数据契约审核', '预算审批审核'],
  ['实际新增资格审核', '合法实施权限审核'],
  ['冻结版本/N/护栏阈值', '目标人群/权益/日期版本'],
  ['成熟经营window HB（天）', '分组N/缺测/power来源'],
];
inputRows.forEach((labels, i) => {
  const r = 8+i;
  value(monitor, `B${r}:C${r}`, labels[0]); value(monitor, `F${r}:G${r}`, labels[1]);
  value(monitor, `D${r}:E${r}`, null); value(monitor, `H${r}:I${r}`, null);
  [ `D${r}:E${r}`, `H${r}:I${r}` ].forEach(x => { monitor.getRange(x).format.fill = amber; monitor.getRange(x).format.borders = { bottom: { style: 'thin', color: '#D7B875' } }; });
  rowHeight(monitor, r, 24);
});
['D12', 'H12', 'D13', 'H13'].forEach(a => { monitor.getRange(a).dataValidation = { rule: { type: 'list', values: ['未核', '通过', '不通过'] } }; });
monitor.getRange('D8:D11').setNumberFormat('0.00'); monitor.getRange('H8:H9').setNumberFormat('0.00');
const mandatory = ['D8','H8','D9','H9','D10','H10','D11','H11','D12','H12','D13','H13','D14','H14','D15','H15'];
const blanks = mandatory.map(x => `OR(ISBLANK(${x}),AND(ISTEXT(${x}),LEN(TRIM(${x}))=0))`).join(',');
const numericValid = 'AND(ISNUMBER(D8),D8>=0,ISNUMBER(H8),H8>0,ISNUMBER(D9),D9>0,ISNUMBER(H9),H9>0,ISNUMBER(D10),D10>=0,D10=INT(D10),ISNUMBER(D11),D11>=0,ISNUMBER(D15),D15>0)';
const metadataValid = 'AND(ISTEXT(H10),ISTEXT(H11),ISTEXT(D14),ISTEXT(H14),ISTEXT(H15))';
monitor.getRange('B5').formulas = [[`=IF(OR(D12="不通过",H12="不通过",D13="不通过",H13="不通过"),"红色：停止当前方案",IF(OR(${blanks}),"黄色：未就绪",IF(NOT(AND(${numericValid},${metadataValid})),"红色：输入口径无效",IF(AND(D12="通过",H12="通过",D13="通过",H13="通过"),"绿色：可提交受限验证审批","黄色：需复核输入"))))`]];
statusFormatting(monitor.getRange('B5:I5'));
value(monitor, 'B16:I16', '契约：原组全员含零用、同窗同币种、分配识别；贡献扣退款及非AI费，服务费含双臂失败及购买后使用。失访不记0。来源/审核须人工复核。');
rowHeight(monitor, 16, 29); rowHeight(monitor, 17, 8);
section(monitor, 18, '未来数据来自授权事件与账单。当前指标值均未测。CI为预设置信区间。');
['指标 / 当前', '定义与未来来源', 'Green / Yellow / Red 规则', '行动与解释边界'].forEach((x, i) => value(monitor, ['B19:C19','D19:E19','F19:G19','H19:I19'][i], x));
monitor.getRange('B19:I19').format = { fill: navy, font: { name: font, size: 10, color: '#FFFFFF', bold: true } }; rowHeight(monitor, 19, 24);
const kpis = [
  ['Primary：延后迁移盲评\n未测 / 黄色', '授权分配与盲评；全员含零用。\n前测调整、延后未练任务差（分）。失访不记0。', '绿：95%CI下限≥冻结受益门槛。\n黄：未成熟/CI跨门槛。\n红：充分精度且上限<受益门槛。', '绿：缺测敏感度不翻转、护栏过。\n黄：补评估/保持预案。\n红：停止当前处理学习论证。'],
  ['机制：有效练习\n未测 / 黄色', '资格、完成及质量事件。\n有效通话人数/全部分配资格账户；分钟/全员。', '绿：质量合格且达冻结机制目标。\n黄：日志缺失/定义未冻。\n红：质量定义或分配数据失效。', '诊断采用、零用和失败。\n机制改善不代替学习或经营效果。'],
  ['课程完成护栏\n未测 / 黄色', '授权课程完成事件。\n全部原分配账户同窗完成量/率的组间差。', '绿：CI下限≥−冻结容忍损失。\n黄：CI跨护栏/窗口未成熟。\n红：CI上限<−容忍损失。', '绿：课程挤出护栏可接受。\n红：暂停，排查练习替代。'],
  ['投诉与技术失败护栏\n未测 / 黄色', '工单、失败/重试事件。\n投诉按分配账户；失败按尝试次数。严重事件独列。', '绿：率CI上限≤冻结上限。\n黄：缺报/CI跨上限。\n红：率CI下限>上限或严重事件。', '红：立即暂停相关处理并排查。\n不以成功完成者作分母。'],
  ['完整服务费用护栏\n未测 / 黄色', '真实服务账单与事件映射。\n双臂含对照、失败、重试及购买后调用，按全员核算。', '绿：完整投入上界≤批准预算。\n黄：币种/账单/映射缺失。\n红：突破预算或账单无法对账。', '预算含服务、其他及新增F。\ncap仅限赠送工作量。总费用另核。'],
  ['经营与政策净值\n未测 / 黄色', '同窗成熟账单、退款、费用。\nΔv=(mT−mC)−(cT−cC)。互斥原层；其他层不设零。', '绿：完整政策净值下界≥0且护栏过。\n黄：传播/N/F缺失或CI跨0。\n红：完整净值上界<0。', '盈利Scale需部署/曝光范围匹配。\n教学投入另按批准预算与学习护栏。'],
];
kpis.forEach((k, i) => {
  const r = 20+i;
  ['B:C','D:E','F:G','H:I'].forEach((span,j) => { const [a,b] = span.split(':'); value(monitor, `${a}${r}:${b}${r}`, k[j]); });
  monitor.getRange(`B${r}:I${r}`).format.borders = { bottom: { style: 'thin', color: '#D8E0E3' } };
  monitor.getRange(`B${r}:C${r}`).format.fill = amber;
  rowHeight(monitor, r, 60);
});
rowHeight(monitor, 26, 8);
value(monitor, 'B27:I28', '运营更新：拟在事件每日质检、费用按账单成熟度复核、学习与经营按各自冻结窗口评审。负责人由未来合作方指定。缺数据或窗口未成熟保持黄色，不用0值或绿色替代。');
rowHeight(monitor, 27, 17); rowHeight(monitor, 28, 17);
value(monitor, 'B29:I30', '依据：Stage4 v2核算契约、Stage5决策卡与事件表。M011/M012仅作机制参考；旧M014的90天/USD不沿用。当前未执行、未联网刷新、未批准扩张。');
rowHeight(monitor, 29, 17); rowHeight(monitor, 30, 17);

// Test meaningful readiness transitions in the same calculation engine, then restore every input.
const fixture = { D8:0, H8:4, D9:1, H9:30, D10:2, H10:'TEST', D11:0, H11:'QA fixture only', D12:'通过', H12:'通过', D13:'通过', H13:'通过', D14:'QA frozen', H14:'QA scope', D15:60, H15:'QA power' };
const cases = [];
function currentStatus() { wb.recalculate(); return monitor.getRange('B5').values[0][0]; }
function assertStatus(name, expected) { const actual = currentStatus(); if(actual !== expected) throw new Error(`${name}: ${actual} != ${expected}`); cases.push({name, expected, actual}); }
assertStatus('all_inputs_blank', '黄色：未就绪');
for (const [cell, v] of Object.entries(fixture)) monitor.getRange(cell).values = [[v]];
assertStatus('complete_fixture_zero_baseline_zero_approved_budget', '绿色：可提交受限验证审批');
monitor.getRange('H10').values = [[null]]; assertStatus('missing_currency_cannot_green', '黄色：未就绪');
monitor.getRange('H10').values = [[' ']]; assertStatus('whitespace_currency_cannot_green', '黄色：未就绪');
monitor.getRange('H10').values = [[0]]; assertStatus('numeric_currency_invalid', '红色：输入口径无效');
monitor.getRange('H10').values = [['TEST']]; monitor.getRange('D12').values = [[null]]; assertStatus('missing_contract_cannot_green', '黄色：未就绪');
monitor.getRange('D12').values = [['通过']]; monitor.getRange('H12').values = [[null]]; assertStatus('missing_budget_approval_cannot_green', '黄色：未就绪');
monitor.getRange('H12').values = [['通过']]; monitor.getRange('D9').values = [[0]]; assertStatus('zero_mde_invalid', '红色：输入口径无效');
monitor.getRange('D9').values = [[1]]; monitor.getRange('H13').values = [['不通过']]; monitor.getRange('D8').values = [[null]]; assertStatus('failed_permission_even_with_other_blank', '红色：停止当前方案');
for (const cell of mandatory) monitor.getRange(cell).values = [[null]];
assertStatus('final_restore_all_blank', '黄色：未就绪');
if (evidence.getRange('B5').values[0][0] !== '黄色：未就绪') throw new Error('Linked overview status stale.');
wb.recalculate();
const errors = await wb.inspect({ kind:'match', searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!', options:{useRegex:true,maxResults:30}, maxChars:3000 });
const inspect = await wb.inspect({kind:'table', range:'未来KPI!B5:I15', include:'values,formulas', tableMaxRows:11, tableMaxCols:8, maxChars:4500});
const series = chart.series.items.map(s => ({formula:s.formula, categoryFormula:s.categoryFormula}));
await fs.writeFile(path.join(qaDir, 'monitoring_artifact_qa.json'), JSON.stringify({engine:'@oai/artifact-tool bundled runtime',cases,errors:errors.ndjson,inspect:inspect.ndjson,series,provenance,actualDataUntouched:true}, null,2));
const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(path.join(root, 'reports/strategy_dashboard.xlsx'));
const companion = path.join(root,'reports/strategy_dashboard.xlsx.inspect.ndjson');
try { await fs.copyFile(companion,path.join(qaDir,'monitoring_saved_inspect.ndjson')); await fs.unlink(companion); }
catch (error) { if(error.code !== 'ENOENT') throw error; }
for (const [sheet, end, file] of [[evidence,40,'monitoring_evidence.png'], [monitor,30,'monitoring_kpi.png']]) {
  const preview = await wb.render({sheetName:sheet.name,range:`A1:J${end}`,scale:1.5,format:'png',headers:false});
  await fs.writeFile(path.join(qaDir, file), new Uint8Array(await preview.arrayBuffer()));
}
console.log(JSON.stringify({workbook:'reports/strategy_dashboard.xlsx',sheets:2,status:'黄色：未就绪',boundaryTests:cases.length,nativeCharts:series.length,previewDir:qaDir}));
