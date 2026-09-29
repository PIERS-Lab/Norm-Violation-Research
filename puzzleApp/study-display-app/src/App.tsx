import { useState } from 'react'
import './App.css'
import base from '../../Puzzles/base_puzzle.png'

// Constructs the blocks for any sub-elements.
  function SubHeader({ text })
{
  return(
  <div className="block"> {text}</div>
  ) 
}
// display the image for the orders
// This is using data gotten from the server so there's an image, alt text, and the scores
function setOrder({ order })
{
  return <img src = {order.img} alt = {order.text} height={800} width={400}/> 
}

function setCount( {count} )
{
  return count
}


function setScores( { scores } )
{
  return scores
}


// main starting point for the app
function App() {
  const [count, setCount] = useState(1)
  const [order, setOrder] = useState(null)
  const [scores, setScores] = useState([0, 0, 0])
  let name, orderNum;
  name = "Bill"
  orderNum = ("Order Number: " + count) 
  return <>
  { /* div is a formatless directive, use if you want to make a custom object */ }
  <div className= 'titleHead'>
    Big Delivery Co.
  </div> 
  { /* flex forces the entire object to print on one line, both headers would be stacked vertically otherwise. */}
  
  <div style={{display:'flex'}}>
    <SubHeader text = {name}/> 
    <SubHeader text = {orderNum}/>
  </div>
  { /* place the image under all the header info via load order */ }
  {/* for next session, have the response to server info be to edit the image and scores, then incerement the counter*/}
  <div>
    <img src = {base} alt = "Base puzzle" height={800} width={600} />
  </div>


  </>

}
// This makes the app fuction the starting point for the program
export default App
