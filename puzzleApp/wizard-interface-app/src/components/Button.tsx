export default function Button({text, onClick, type = "button"})
{
    return(
        <button type = {type} onClick={onClick} className="inputButtn"> {
            {text}
        }
        </button>
    );
}    