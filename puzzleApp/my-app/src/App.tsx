import { useState } from 'react'
import './App.css'
import base from '../../Puzzles/base_puzzle.png' 
  function SubHeader({ text })
{
  return(
  <div className="block"> {text}</div>
  ) 
}

function order({ image, text })
{
  return <img src = {image} alt = {text} height={800} width={400 }/> 
}
function App() {
  const [count, setCount] = useState(1)
  let name, orderNum;
  name = "Bill"
  orderNum = ("Order Number: " + count) 
  return <>
  <div className= 'titleHead'>
    Big Delivery Co.
  </div> 
  <div style={{display:'flex'}}>
    <SubHeader text = {name}/> 
    <SubHeader text = {orderNum}/>
  </div>
  <div>
    <img src = {base} alt = "Base puzzle" height={800} width={600} />
  </div>

  </>

}

export default App
