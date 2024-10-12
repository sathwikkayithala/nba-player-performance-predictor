import Link from 'next/link';
import './home.css';

export default function Home() {
    return (
        <div className="container">
            <h1 className="title">Welcome to the Player Performance Predictor</h1>
            <Link href="/predictions" className="button">
                Check out the player stat prediction for the upcoming and previous years!
            </Link>
        </div>
    );
}
