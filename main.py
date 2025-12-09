<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Pro Crypto Calculator — Paul Sode</title>
<style>
  :root { --bg: #0b0e11; --card: #1e2329; --text: #eaecef; --accent: #fcd535; --green: #0ecb81; --red: #f6465d; }
  body { font-family: 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); padding: 20px; max-width: 600px; margin: auto; }
  h2 { border-bottom: 2px solid var(--accent); padding-bottom: 10px; margin-bottom: 20px; color: var(--accent); }
  
  /* Input Styling */
  .card { background: var(--card); padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
  input, select { background: #2b3139; border: 1px solid #474d57; color: white; padding: 10px; border-radius: 4px; width: 100%; box-sizing: border-box; font-size: 1rem; margin-top: 5px; }
  label { font-size: 0.85rem; color: #848e9c; margin-top: 15px; display: block; font-weight: 600; }
  
  /* Grid Layout */
  .row { display: flex; gap: 15px; }
  .col { flex: 1; }
  
  /* Buttons */
  button { background: var(--accent); color: #000; border: none; padding: 12px; width: 100%; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 1rem; margin-top: 25px; transition: 0.2s; }
  button:hover { opacity: 0.9; transform: translateY(-1px); }

  /* Results Area */
  #result-area { margin-top: 20px; display: none; }
  .result-card { background: var(--card); padding: 15px; border-radius: 8px; border-left: 4px solid var(--accent); margin-bottom: 10px; }
  .res-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9rem; }
  .val { font-weight: bold; font-family: monospace; font-size: 1.1rem; }
  .green { color: var(--green); }
  .red { color: var(--red); }
  .sub-text { font-size: 0.8rem; color: #848e9c; }
</style>
</head>
<body>

<h2>🚀 Trade Calculator <span style="font-size:0.6em; color:#848e9c">by Paul Sode</span></h2>

<div class="card">
  <div class="row">
    <div class="col">
      <label>Coin Symbol</label>
      <input id="coin" value="BTC" placeholder="e.g. BTC" />
    </div>
    <div class="col">
      <label>Side (Long/Short)</label>
      <select id="side">
        <option value="long">🟢 LONG (Buy)</option>
        <option value="short">🔴 SHORT (Sell)</option>
      </select>
    </div>
  </div>

  <div class="row">
    <div class="col">
      <label>Margin ($)</label>
      <input id="margin" type="number" value="100" />
    </div>
    <div class="col">
      <label>Leverage (x)</label>
      <input id="leverage" type="number" value="10" />
    </div>
  </div>

  <div class="row">
    <div class="col">
      <label>Entry Price ($)</label>
      <input id="entry" type="number" value="60000" />
    </div>
    <div class="col">
      <label>Fee % (Total)</label>
      <input id="fee" type="number" step="0.01" value="0.1" title="Exchange fee" />
    </div>
  </div>

  <div class="row">
    <div class="col">
      <label>Target Price ($)</label>
      <input id="target" type="number" value="62000" placeholder="Take Profit" />
    </div>
    <div class="col">
      <label>Stop Loss ($)</label>
      <input id="stop" type="number" value="59000" placeholder="Stop Loss" />
    </div>
  </div>

  <button id="calc">CALCULATE PnL</button>
</div>

<div id="result-area">
  
  <div class="result-card" style="border-color: #474d57;">
    <div class="res-row"><span>Position Size:</span> <span class="val" id="res-size"></span></div>
    <div class="res-row"><span>Liquidation Price:</span> <span class="val" style="color:orange" id="res-liq"></span></div>
    <div class="res-row"><span>Fees (Est):</span> <span class="val" style="color:#f6465d" id="res-fees"></span></div>
  </div>

  <div class="result-card" style="border-color: var(--green);">
    <div class="res-row"><span>Target Result:</span> <span class="sub-text">If price hits target</span></div>
    <div class="res-row"><span>Net Profit:</span> <span class="val green" id="res-win-pnl"></span></div>
    <div class="res-row"><span>ROI:</span> <span class="val green" id="res-win-roi"></span></div>
  </div>

  <div class="result-card" style="border-color: var(--red);">
    <div class="res-row"><span>Stop Loss Result:</span> <span class="sub-text">If price hits stop</span></div>
    <div class="res-row"><span>Net Loss:</span> <span class="val red" id="res-loss-pnl"></span></div>
    <div class="res-row"><span>ROI:</span> <span class="val red" id="res-loss-roi"></span></div>
  </div>

</div>

<script>
// Format currency Helper
const fmt = (num) => '$' + Number(num).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

document.getElementById('calc').addEventListener('click', () => {
  // 1. Get Inputs
  const margin = parseFloat(document.getElementById('margin').value) || 0;
  const leverage = parseFloat(document.getElementById('leverage').value) || 1;
  const entry = parseFloat(document.getElementById('entry').value) || 0;
  const target = parseFloat(document.getElementById('target').value) || 0;
  const stop = parseFloat(document.getElementById('stop').value) || 0;
  const feePct = parseFloat(document.getElementById('fee').value) || 0;
  const isLong = document.getElementById('side').value === 'long';

  if(entry === 0) return alert("Please enter an Entry Price");

  // 2. Core Math
  const positionValue = margin * leverage;
  const coins = positionValue / entry;
  
  // Calculate Liquidation (Approximate)
  // Long: Entry - (Margin / Coins) | Short: Entry + (Margin / Coins)
  let liqPrice = isLong ? (entry - (margin / coins)) : (entry + (margin / coins));
  if (liqPrice < 0) liqPrice = 0; // Price can't be negative

  // Calculate Fees (Open + Close estimate)
  // Fee = (EntryValue * %) + (ExitValue * %) - simplified to 2x entry for estimation
  const totalFees = (positionValue * (feePct / 100)) * 2; 

  // Function to calculate PnL for a specific price
  function calculatePnL(exitPrice) {
    let grossPnL = 0;
    if (isLong) {
      grossPnL = (exitPrice - entry) * coins;
    } else {
      grossPnL = (entry - exitPrice) * coins;
    }
    const netPnL = grossPnL - totalFees;
    const roi = (netPnL / margin) * 100;
    return { net: netPnL, roi: roi };
  }

  const winStats = calculatePnL(target);
  const lossStats = calculatePnL(stop);

  // 3. Display Results
  document.getElementById('result-area').style.display = 'block';
  
  document.getElementById('res-size').textContent = fmt(positionValue) + ` (${coins.toFixed(4)} Coins)`;
  document.getElementById('res-liq').textContent = fmt(liqPrice);
  document.getElementById('res-fees').textContent = '-' + fmt(totalFees);

  // Win Stats
  document.getElementById('res-win-pnl').textContent = (winStats.net >= 0 ? '+' : '') + fmt(winStats.net);
  document.getElementById('res-win-roi').textContent = winStats.roi.toFixed(2) + '%';
  
  // Loss Stats
  document.getElementById('res-loss-pnl').textContent = fmt(lossStats.net);
  document.getElementById('res-loss-roi').textContent = lossStats.roi.toFixed(2) + '%';
});
</script>
</body>
</html>
