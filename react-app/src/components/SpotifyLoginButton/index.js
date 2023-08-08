import { useDispatch } from 'react-redux';
import { spotifyLogin } from "../../store/session";
import './SpotifyLoginButton.css';

function SpotifyLoginButton() {
    const dispatch = useDispatch();

    const handleClick = async(e) => {
        e.preventDefault();
        await dispatch(spotifyLogin);
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
