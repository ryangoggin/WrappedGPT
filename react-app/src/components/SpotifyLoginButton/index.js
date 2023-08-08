import { useDispatch } from 'react-redux';
import './SpotifyLoginButton.css';

function SpotifyLoginButton() {
    const dispatch = useDispatch();

    const handleClick = async(e) => {
        e.preventDefault();
        // need to make thunk to request spotify authorization
    }

    return (
        <>
            <button onClick={handleClick}>
                Login to Spotify
            </button>
        </>
    );
}

export default SpotifyLoginButton;
