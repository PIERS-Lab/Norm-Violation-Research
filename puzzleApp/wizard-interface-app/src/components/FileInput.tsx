export default function FileInput({ onFileSelect }) 
{   
   function handleFileChange(event) {
        let file = event.target.files[0]
        if (file) {
            onFileSelect(file)
        }
    }
    return (<div>
        <input type="file" onChange={ handleFileChange }/>         
    </div>)
}

