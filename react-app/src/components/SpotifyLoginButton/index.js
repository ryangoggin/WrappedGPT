import { useDispatch } from 'react-redux';
import { spotifyLogin } from "../../store/spotify";
import './SpotifyLoginButton.css';
import { useEffect, useState } from 'react';

function SpotifyLoginButton() {
    const dispatch = useDispatch();
    const [accessToken, setAccessToken] = useState("");

    // useEffect to get accessToken if it exists and store in local storage
    useEffect(() => {
        if (!accessToken) {
            console.log("there isn't an access token...")
        }
    }, [])

    const handleClick = async(e) => {
        e.preventDefault();
        await dispatch(spotifyLogin());
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
